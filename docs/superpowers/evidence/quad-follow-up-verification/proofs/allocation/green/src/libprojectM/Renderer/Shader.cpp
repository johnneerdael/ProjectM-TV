#include "Shader.hpp"

#include <glm/gtc/type_ptr.hpp>

#include <atomic>
#include <list>
#include <mutex>
#include <vector>

namespace libprojectM {
namespace Renderer {

namespace {

// Program bound on this thread's context, to skip redundant glUseProgram calls (each one makes the
// driver validate its state again at the next draw call).
constexpr GLuint unknownProgram = ~0u;
thread_local GLuint boundProgram = unknownProgram;

// Linked program binaries by shader source, shared by all projectM instances in the process. A
// program that was linked before (by any instance, on any thread) is loaded with glProgramBinary
// in milliseconds instead of being compiled again, which can take hundreds of milliseconds.
class ProgramCache
{
public:
    static constexpr size_t maxBytes = 8 * 1024 * 1024;

    static auto Instance() -> ProgramCache&
    {
        static ProgramCache cache;
        return cache;
    }

    auto Load(GLuint program, const std::string& key) -> bool
    {
#ifdef USE_GLES
        GLenum format{};
        std::vector<char> binary;
        {
            std::lock_guard<std::mutex> lock(m_mutex);
            auto it = Find(key);
            if (it == m_entries.end())
            {
                m_misses++;
                return false;
            }
            format = it->format;
            binary = it->binary;
            m_entries.splice(m_entries.begin(), m_entries, it);
        }
        glProgramBinary(program, format, binary.data(), static_cast<GLsizei>(binary.size()));
        GLint linked{GL_FALSE};
        glGetProgramiv(program, GL_LINK_STATUS, &linked);
        std::lock_guard<std::mutex> lock(m_mutex);
        if (linked == GL_TRUE)
        {
            m_hits++;
            return true;
        }
        auto it = Find(key); // rejected by the driver: compile normally
        if (it != m_entries.end())
        {
            m_bytes -= it->key.size() + it->binary.size();
            m_entries.erase(it);
        }
        m_misses++;
#else
        (void) program;
        (void) key;
#endif
        return false;
    }

    void Store(GLuint program, const std::string& key)
    {
#ifdef USE_GLES
        GLint length{};
        glGetProgramiv(program, GL_PROGRAM_BINARY_LENGTH, &length);
        if (length <= 0 || static_cast<size_t>(length) > maxBytes / 4)
        {
            return;
        }
        Entry entry{key, 0, std::vector<char>(static_cast<size_t>(length))};
        GLsizei written{};
        glGetProgramBinary(program, length, &written, &entry.format, entry.binary.data());
        if (written <= 0)
        {
            return;
        }
        entry.binary.resize(static_cast<size_t>(written));

        std::lock_guard<std::mutex> lock(m_mutex);
        auto it = Find(key);
        if (it != m_entries.end())
        {
            m_bytes -= it->key.size() + it->binary.size();
            m_entries.erase(it);
        }
        m_bytes += entry.key.size() + entry.binary.size(); // the key is the full shader source
        m_entries.push_front(std::move(entry));
        while (m_bytes > maxBytes && !m_entries.empty())
        {
            m_bytes -= m_entries.back().key.size() + m_entries.back().binary.size();
            m_entries.pop_back();
        }
#else
        (void) program;
        (void) key;
#endif
    }

    void Stats(uint32_t& hits, uint32_t& misses)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        hits = m_hits;
        misses = m_misses;
    }

private:
    struct Entry
    {
        std::string key;
        GLenum format;
        std::vector<char> binary;
    };

    auto Find(const std::string& key) -> std::list<Entry>::iterator
    {
        for (auto it = m_entries.begin(); it != m_entries.end(); ++it)
        {
            if (it->key == key)
            {
                return it;
            }
        }
        return m_entries.end();
    }

    std::mutex m_mutex;
    std::list<Entry> m_entries; //!< Most recently used first.
    size_t m_bytes{};
    uint32_t m_hits{};
    uint32_t m_misses{};
};

} // namespace

void Shader::ProgramCacheStats(uint32_t& hits, uint32_t& misses)
{
    ProgramCache::Instance().Stats(hits, misses);
}

Shader::Shader()
    : m_shaderProgram(glCreateProgram())
{
}

Shader::~Shader()
{
    if (m_shaderProgram)
    {
        if (boundProgram == m_shaderProgram)
        {
            boundProgram = unknownProgram;
        }
        glDeleteProgram(m_shaderProgram);
    }
}

void Shader::CompileProgram(const std::string& vertexShaderSource,
                            const std::string& fragmentShaderSource)
{
    m_uniformLocations.clear();
    std::string cacheKey = vertexShaderSource + '\0' + fragmentShaderSource;
    if (ProgramCache::Instance().Load(m_shaderProgram, cacheKey))
    {
        return;
    }

    auto vertexShader = CompileShader(vertexShaderSource, GL_VERTEX_SHADER);
    GLuint fragmentShader{};
    try
    {
        fragmentShader = CompileShader(fragmentShaderSource, GL_FRAGMENT_SHADER);
    }
    catch (...)
    {
        // The vertex shader is still unattached, so deleting the program cannot release it.
        glDeleteShader(vertexShader);
        throw;
    }

    glAttachShader(m_shaderProgram, vertexShader);
    glAttachShader(m_shaderProgram, fragmentShader);

#ifdef USE_GLES
    glProgramParameteri(m_shaderProgram, GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE);
#endif
    glLinkProgram(m_shaderProgram);

    // Shader objects are no longer needed after linking, free the memory.
    glDetachShader(m_shaderProgram, vertexShader);
    glDetachShader(m_shaderProgram, fragmentShader);
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);

    GLint programLinked;
    glGetProgramiv(m_shaderProgram, GL_LINK_STATUS, &programLinked);
    if (programLinked == GL_TRUE)
    {
        ProgramCache::Instance().Store(m_shaderProgram, cacheKey);
        return;
    }

    GLint infoLogLength{};
    glGetProgramiv(m_shaderProgram, GL_INFO_LOG_LENGTH, &infoLogLength);
    std::vector<char> message(infoLogLength + 1);
    glGetProgramInfoLog(m_shaderProgram, infoLogLength, nullptr, message.data());

    throw ShaderException("Error compiling shader: " + std::string(message.data()));
}

bool Shader::Validate(std::string& validationMessage) const
{
    GLint result{GL_FALSE};
    int infoLogLength;

    glValidateProgram(m_shaderProgram);

    glGetProgramiv(m_shaderProgram, GL_VALIDATE_STATUS, &result);
    glGetProgramiv(m_shaderProgram, GL_INFO_LOG_LENGTH, &infoLogLength);
    if (infoLogLength > 0)
    {
        std::vector<char> validationErrorMessage(infoLogLength + 1);
        glGetProgramInfoLog(m_shaderProgram, infoLogLength, nullptr, validationErrorMessage.data());
        validationMessage = std::string(validationErrorMessage.data());
    }

    return result;
}

void Shader::Bind() const
{
    if (m_shaderProgram > 0 && boundProgram != m_shaderProgram)
    {
        glUseProgram(m_shaderProgram);
        boundProgram = m_shaderProgram;
    }
}

void Shader::Unbind()
{
    glUseProgram(0);
    boundProgram = 0;
}

void Shader::InvalidateBoundProgram()
{
    boundProgram = unknownProgram;
}

auto Shader::UniformLocation(const char* uniform) const -> GLint
{
    auto it = m_uniformLocations.find(uniform);
    if (it != m_uniformLocations.end())
    {
        return it->second;
    }
    auto location = glGetUniformLocation(m_shaderProgram, uniform);
    m_uniformLocations.emplace(uniform, location);
    return location;
}

void Shader::SetUniformFloat(const char* uniform, float value) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform1fv(location, 1, &value);
}

void Shader::SetUniformInt(const char* uniform, int value) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform1iv(location, 1, &value);
}

void Shader::SetUniformFloat2(const char* uniform, const glm::vec2& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform2fv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformInt2(const char* uniform, const glm::ivec2& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform2iv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformFloat3(const char* uniform, const glm::vec3& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform3fv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformInt3(const char* uniform, const glm::ivec3& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform3iv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformFloat4(const char* uniform, const glm::vec4& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform4fv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformInt4(const char* uniform, const glm::ivec4& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniform4iv(location, 1, glm::value_ptr(values));
}

void Shader::SetUniformMat3x4(const char* uniform, const glm::mat3x4& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniformMatrix3x4fv(location, 1, GL_FALSE, glm::value_ptr(values));
}

void Shader::SetUniformMat4x4(const char* uniform, const glm::mat4x4& values) const
{
    auto location = UniformLocation(uniform);
    if (location < 0)
    {
        return;
    }
    glUniformMatrix4fv(location, 1, GL_FALSE, glm::value_ptr(values));
}

GLuint Shader::CompileShader(const std::string& source, GLenum type)
{
    GLint shaderCompiled{};

    auto shader = glCreateShader(type);
    const auto* shaderSourceCStr = source.c_str();
    glShaderSource(shader, 1, &shaderSourceCStr, nullptr);

    glCompileShader(shader);

    glGetShaderiv(shader, GL_COMPILE_STATUS, &shaderCompiled);
    if (shaderCompiled == GL_TRUE)
    {
        return shader;
    }

    GLint infoLogLength{};
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &infoLogLength);
    std::vector<char> message(infoLogLength + 1);
    glGetShaderInfoLog(shader, infoLogLength, nullptr, message.data());
    glDeleteShader(shader);

    throw ShaderException("Error compiling shader: " + std::string(message.data()));
}

auto Shader::GetShaderLanguageVersion() -> Shader::GlslVersion
{
    const char* shaderLanguageVersion = reinterpret_cast<const char*>(glGetString(GL_SHADING_LANGUAGE_VERSION));

    if (shaderLanguageVersion == nullptr)
    {
        return {};
    }

    std::string shaderLanguageVersionString(shaderLanguageVersion);

    // Some OpenGL implementations add non-standard-conforming text in front, e.g. WebGL, which returns "OpenGL ES GLSL ES 3.00 ..."
    // Find the first digit and start there.
    auto firstDigit = shaderLanguageVersionString.find_first_of("0123456789");
    if (firstDigit != std::string::npos && firstDigit != 0)
    {
        shaderLanguageVersionString = shaderLanguageVersionString.substr(firstDigit);
    }

    // Cut off the vendor-specific information, if any
    auto spacePos = shaderLanguageVersionString.find(' ');
    if (spacePos != std::string::npos)
    {
        shaderLanguageVersionString.resize(spacePos);
    }

    auto dotPos = shaderLanguageVersionString.find('.');
    if (dotPos == std::string::npos)
    {
        return {};
    }

    int versionMajor = std::stoi(shaderLanguageVersionString.substr(0, dotPos));
    int versionMinor = std::stoi(shaderLanguageVersionString.substr(dotPos + 1));

    return {versionMajor, versionMinor};
}

} // namespace Renderer
} // namespace libprojectM
