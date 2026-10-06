#include "TextureSamplerDescriptor.hpp"

#include "TextureManager.hpp"
#include "Utils.hpp"

#include <utility>

namespace libprojectM {
namespace Renderer {

namespace {
// Preserve spelling and mode qualification while deriving the emitted shorthand.
auto ShortRandomAlias(const std::string& name) -> std::string
{
    const size_t offset = name.size() > 3 && name[2] == '_' ? 3 : 0;
    const auto base = Utils::ToLower(name.substr(offset));
    if (base.size() > 7 && base.substr(0, 4) == "rand" && base[6] == '_')
    {
        return name.substr(0, offset + 6);
    }
    return {};
}
} // namespace

TextureSamplerDescriptor::TextureSamplerDescriptor(const std::shared_ptr<class Texture>& texture,
                                                   const std::shared_ptr<class Sampler>& sampler,
                                                   std::string samplerName,
                                                   std::string sizeName)
    : m_texture(texture)
    , m_sampler(sampler)
    , m_samplerName(std::move(samplerName))
    , m_sizeName(std::move(sizeName))
{
}

auto TextureSamplerDescriptor::Empty() const -> bool
{
    return !m_texture || m_texture->Empty();
}

void TextureSamplerDescriptor::Bind(GLint unit, const Shader& shader) const
{

    if (m_texture && m_sampler)
    {
        m_texture->Bind(unit, m_sampler);

        shader.SetUniformInt(std::string("sampler_" + m_samplerName).c_str(), unit);
        // SamplerDeclaration also emits the short alias for a prefixed random texture.
        if (const auto shortName = ShortRandomAlias(m_samplerName); !shortName.empty())
        {
            shader.SetUniformInt(std::string("sampler_" + shortName).c_str(), unit);
        }
        // Might be setting this more than once if the texture is used with different wrap/filter modes, but this rarely happens.
        shader.SetUniformFloat4(std::string("texsize_" + m_sizeName).c_str(), {m_texture->Width(),
                                                                               m_texture->Height(),
                                                                               1.0f / static_cast<float>(m_texture->Width()),
                                                                               1.0f / static_cast<float>(m_texture->Height())});
        // Bind shorthand random texture size uniform
        if (const auto shortName = ShortRandomAlias(m_sizeName); !shortName.empty())
        {
            shader.SetUniformFloat4(std::string("texsize_" + shortName).c_str(), {m_texture->Width(),
                                                                                                m_texture->Height(),
                                                                                                1.0f / static_cast<float>(m_texture->Width()),
                                                                                                1.0f / static_cast<float>(m_texture->Height())});
        }
    }
}

void TextureSamplerDescriptor::Unbind(GLint unit)
{
    if (m_texture)
    {
        m_texture->Unbind(unit);
    }
    Sampler::Unbind(unit);
}

auto TextureSamplerDescriptor::Texture() const -> std::shared_ptr<class Texture>
{
    return m_texture;
}

void TextureSamplerDescriptor::Texture(const std::shared_ptr<Renderer::Texture>& texture)
{
    m_texture = texture;
}

void TextureSamplerDescriptor::Texture(const std::weak_ptr<Renderer::Texture>& texture)
{
    m_texture = texture.lock();
}

auto TextureSamplerDescriptor::Sampler() const -> std::shared_ptr<class Sampler>
{
    return m_sampler;
}

auto TextureSamplerDescriptor::SamplerDeclaration() const -> std::string
{
    if (!m_texture || !m_sampler)
    {
        return {};
    }

    std::string declaration = "uniform ";
    if (m_texture->Type() == GL_TEXTURE_3D)
    {
        declaration.append("sampler3D sampler_");
    }
    else
    {
        declaration.append("sampler2D sampler_");
    }
    declaration.append(m_samplerName);
    declaration.append(";\n");

    // Add short sampler name for prefixed random textures.
    // E.g. "sampler_rand00" if a sampler "sampler_rand00_smalltiled" was declared
    if (const auto shortName = ShortRandomAlias(m_samplerName); !shortName.empty())
    {
        declaration.append("uniform sampler2D sampler_");
        declaration.append(shortName);
        declaration.append(";\n");
    }

    return declaration;
}

auto TextureSamplerDescriptor::TexSizeDeclaration() const -> std::string
{
    if (!m_texture || !m_sampler)
    {
        return {};
    }

    std::string declaration;
    if (!m_sizeName.empty())
    {
        declaration.append("uniform float4 texsize_");
        declaration.append(m_sizeName);
        declaration.append(";\n");

        // Add short texsize uniform for prefixed random textures.
        // E.g. "texsize_rand00" if a sampler "sampler_rand00_smalltiled" was declared
        if (const auto shortName = ShortRandomAlias(m_sizeName); !shortName.empty())
        {
            declaration.append("uniform float4 texsize_");
            declaration.append(shortName);
            declaration.append(";\n");
        }
    }

    return declaration;
}

void TextureSamplerDescriptor::TryUpdate(TextureManager& textureManager)
{
    if (!Empty())
    {
        return;
    }

    auto desc = textureManager.GetTexture(m_samplerName);
    if (desc.Empty())
    {
        // Only try once, then give up.
        m_updateFailed = true;
        return;
    }

    m_texture = desc.m_texture;
    m_sampler = desc.m_sampler;
}

} // namespace Renderer
} // namespace libprojectM
