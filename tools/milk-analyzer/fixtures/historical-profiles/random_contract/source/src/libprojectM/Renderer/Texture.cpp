#include "Renderer/Texture.hpp"

#include <algorithm>
#include <deque>
#include <utility>

namespace libprojectM {
namespace Renderer {

namespace {

// Framebuffer textures of discarded presets, kept for the next preset of the same size: creating
// them anew (glTexImage2D) cost the render thread 16-58 ms at a preset switch on an NVIDIA SHIELD.
// Per thread, as textures belong to the thread's context; disabled until the host sets a limit.
class TexturePool
{
public:
    struct Entry
    {
        GLuint id;
        int width;
        int height;
        GLint internalFormat;
        GLenum format;
        GLenum type;
        bool hasMipmaps;
        size_t bytes;
    };

    static auto Instance() -> TexturePool&
    {
        thread_local TexturePool pool;
        return pool;
    }

    auto Take(int width, int height, GLint internalFormat, GLenum format, GLenum type, bool& hasMipmaps) -> GLuint
    {
        for (auto it = m_entries.begin(); it != m_entries.end(); ++it)
        {
            if (it->width == width && it->height == height && it->internalFormat == internalFormat &&
                it->format == format && it->type == type)
            {
                GLuint id = it->id;
                hasMipmaps = it->hasMipmaps;
                m_bytes -= it->bytes;
                m_entries.erase(it);
                return id;
            }
        }
        hasMipmaps = false;
        return 0;
    }

    auto Put(const Entry& entry) -> bool
    {
        if (entry.bytes > m_maxBytes)
        {
            return false;
        }
        m_entries.push_back(entry);
        m_bytes += entry.bytes;
        Trim(m_maxBytes);
        return true;
    }

    void SetLimit(size_t maxBytes)
    {
        m_maxBytes = maxBytes;
        Trim(maxBytes);
    }

    void Forget()
    {
        m_entries.clear();
        m_bytes = 0;
    }

    auto BytesHeld() const -> size_t
    {
        return m_bytes;
    }

private:
    void Trim(size_t maxBytes)
    {
        while (m_bytes > maxBytes && !m_entries.empty()) // oldest first
        {
            glDeleteTextures(1, &m_entries.front().id);
            m_bytes -= m_entries.front().bytes;
            m_entries.pop_front();
        }
    }

    std::deque<Entry> m_entries;
    size_t m_bytes{};
    size_t m_maxBytes{};
};

} // namespace

void Texture::SetPoolable(GLint internalFormat, GLenum format, GLenum type, bool hasMipmaps)
{
    m_poolable = true;
    m_internalFormat = internalFormat;
    m_format = format;
    m_type = type;
    m_hasMipmaps = hasMipmaps;
}

void Texture::GenerateMipmaps()
{
    glBindTexture(m_target, m_textureId);
    glGenerateMipmap(m_target);
    m_hasMipmaps = true;
}

auto Texture::StorageBytes(int width, int height, GLint internalFormat, bool mipmaps) -> size_t
{
    size_t perPixel = 4;
    switch (internalFormat)
    {
        case GL_R8:
        case GL_STENCIL_INDEX8:
            perPixel = 1;
            break;
        case GL_DEPTH_COMPONENT16:
            perPixel = 2;
            break;
        case GL_RGBA16F:
            perPixel = 8;
            break;
        case GL_RGBA32F:
            perPixel = 16;
            break;
        default:
            break;
    }
    size_t pixels = static_cast<size_t>(width) * static_cast<size_t>(height);
    // glGenerateMipmap makes levels down to 1x1, each dimension halved and rounded down (at least 1).
    while (mipmaps && (width > 1 || height > 1))
    {
        width = std::max(1, width / 2);
        height = std::max(1, height / 2);
        pixels += static_cast<size_t>(width) * static_cast<size_t>(height);
    }
    return pixels * perPixel;
}

auto Texture::TakePooled(int width, int height, GLint internalFormat, GLenum format, GLenum type,
                         bool& hasMipmaps) -> GLuint
{
    return TexturePool::Instance().Take(width, height, internalFormat, format, type, hasMipmaps);
}

void Texture::SetPoolLimit(size_t maxBytes)
{
    TexturePool::Instance().SetLimit(maxBytes);
}

void Texture::ForgetPool()
{
    TexturePool::Instance().Forget();
}

auto Texture::PoolBytes() -> size_t
{
    return TexturePool::Instance().BytesHeld();
}

Texture::Texture(std::string name, const int width, const int height, const bool isUserTexture)
    : m_target(GL_TEXTURE_2D)
    , m_name(std::move(name))
    , m_width(width)
    , m_height(height)
    , m_isUserTexture(isUserTexture)
    , m_internalFormat(GL_RGB)
    , m_format(GL_RGB)
    , m_type(GL_UNSIGNED_BYTE)
{
    CreateNewTexture();
}

Texture::Texture(std::string name, int width, int height,
                 GLint internalFormat, GLenum format, GLenum type, bool isUserTexture)
    : m_target(GL_TEXTURE_2D)
    , m_name(std::move(name))
    , m_width(width)
    , m_height(height)
    , m_isUserTexture(isUserTexture)
    , m_internalFormat(internalFormat)
    , m_format(format)
    , m_type(type)
{
    CreateNewTexture();
}

Texture::Texture(std::string name, const GLuint texID, const GLenum target,
                 const int width, const int height, const bool isUserTexture, std::string sourcePath)
    : m_textureId(texID)
    , m_target(target)
    , m_name(std::move(name))
    , m_sourcePath(std::move(sourcePath))
    , m_width(width)
    , m_height(height)
    , m_isUserTexture(isUserTexture)
{
}

Texture::~Texture()
{
    if (m_textureId > 0)
    {
        if (!m_poolable ||
            !TexturePool::Instance().Put({m_textureId, m_width, m_height, m_internalFormat, m_format, m_type, m_hasMipmaps,
                                          StorageBytes(m_width, m_height, m_internalFormat, m_hasMipmaps)}))
        {
            glDeleteTextures(1, &m_textureId);
        }
        m_textureId = 0;
    }
}

void Texture::Bind(GLint slot, const Sampler::Ptr& sampler) const
{
    glActiveTexture(GL_TEXTURE0 + slot);
    glBindTexture(m_target, m_textureId);

    if (sampler)
    {
        sampler->Bind(slot);
    }
}

void Texture::Unbind(GLint slot) const
{
    glActiveTexture(GL_TEXTURE0 + slot);
    glBindTexture(m_target, 0);
}

auto Texture::TextureID() const -> GLuint
{
    return m_textureId;
}

auto Texture::Name() const -> const std::string&
{
    return m_name;
}

auto Texture::SourcePath() const -> const std::string&
{
    return m_sourcePath;
}

auto Texture::Type() const -> GLenum
{
    return m_target;
}

auto Texture::Width() const -> int
{
    return m_width;
}

auto Texture::Height() const -> int
{
    return m_height;
}

auto Texture::IsUserTexture() const -> bool
{
    return m_isUserTexture;
}

auto Texture::Empty() const -> bool
{
    return m_textureId == 0;
}

void Texture::CreateNewTexture()
{
    glGenTextures(1, &m_textureId);
    glBindTexture(m_target, m_textureId);
    glTexImage2D(m_target, 0, m_internalFormat, m_width, m_height, 0, m_format, m_type, nullptr);
    glBindTexture(m_target, 0);
}

} // namespace Renderer
} // namespace libprojectM
