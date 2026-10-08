# Generate a visual witness for ProjectM TV patch 0010

Create a preset and texture-pack test that clearly demonstrates a per-preset texture lookup ownership enhancement. Explain the predicted before/after appearance before it is rendered.

## Classification

Patch 0010 is a host-integration enhancement. Upstream documents changing texture
paths as clearing/reloading its global texture cache; redirecting later lookups
is consistent with that contract. The patch adds retained per-preset paths for
independent custom packs. Do not describe the comparison as an upstream bug or a
MilkDrop rendering-compatibility correction. Original MilkDrop 2.25 custom shapes
use the previous frame as their texture; the named-image shape below is a
projectM capability.

## Target patch

`0010-preset-texture-search-path-ownership.patch`

Source:
https://github.com/johnneerdael/ProjectM-TV/blob/feat/current-4-2-patch-proof/tools/projectm-patches/0010-preset-texture-search-path-ownership.patch

The engine is based on unreleased projectM 4.2 master, commit:
`6f64807467e312034883a4389e6aa80a675458bc`.

## Upstream behavior: live presets use the host's newest texture lookup

Before the patch, `ProjectM` owns one global texture manager:

```cpp
std::unique_ptr<Renderer::TextureManager> m_textureManager;
```

Changing texture roots replaces that manager:

```cpp
void ProjectM::SetTexturePaths(std::vector<std::string> texturePaths)
{
    m_textureSearchPaths = std::move(texturePaths);
    m_textureManager =
        std::make_unique<Renderer::TextureManager>(m_textureSearchPaths);
    // Texture-load callback installation follows.
}
```

During a soft transition, both incoming and outgoing presets receive the same render context, whose texture manager is the current global manager:

```cpp
m_transitioningPreset->RenderFrame(audioData, renderContext);
m_activePreset->RenderFrame(audioData, renderContext);
```

Consequently, a subsequent texture lookup by the outgoing preset can resolve against the incoming pack's roots. The outgoing preset may suddenly display the other pack's image before its fade finishes.

Before the patch, `ResetTextures()` also recreates the global manager using the newest search paths.

## Rendering path that demonstrates the ownership difference

Custom shapes support a named image through the `shapecode_<n>_image` field.

The shape renderer resets its lookup guard when preparing each frame:

```cpp
m_imageLookedUp = false;
```

A textured shape then resolves its image through that frame's texture manager:

```cpp
if (!m_imageLookedUp)
{
    m_imageLookedUp = true;
    m_imageTexture = m_image.empty()
        ? Renderer::TextureSamplerDescriptor()
        : m_presetState.renderContext.textureManager->GetTexture(m_image);
}
```

This repeated named-image lookup is a useful exposure path.

**Important pitfall:** a custom shader that binds its image once at initialization can retain that texture through a strong descriptor. Such a preset may show no ownership difference during the same root-switch test. Do not assume that any named shader sampler will demonstrate the enhancement.

## What the patch changes

The patch gives live presets their own retained texture-manager ownership:

```cpp
std::shared_ptr<Renderer::TextureManager> m_textureManager;
std::shared_ptr<Renderer::TextureManager> m_activeTextureManager;
std::shared_ptr<Renderer::TextureManager> m_transitioningTextureManager;
```

Rendering supplies each preset's retained lookup:

```cpp
auto activeContext = renderContext;
activeContext.textureManager = m_activeTextureManager.get();
m_activePreset->RenderFrame(audioData, activeContext);

auto incomingContext = renderContext;
incomingContext.textureManager = m_transitioningTextureManager.get();
m_transitioningPreset->RenderFrame(audioData, incomingContext);
```

New roots apply to subsequently loaded presets. Existing presets retain their original roots and images until retirement.

Reset clears user-image caches in each distinct live manager while preserving its roots, built-in resources, existing sampler bindings and authored feedback.

## Required exposure scenario

- Pack A and Pack B contain different, immediately recognizable pictures under the same texture basename.
- The outgoing preset uses a textured custom shape that performs the named-image lookup above.
- Make that image large and visually legible.
- The host changes roots from A to B while the outgoing preset remains alive.
- The host then loads the incoming preset with a soft transition.
- Reset textures during the transition.
- A `.milk` preset cannot perform these host API operations itself; describe the required host sequence separately.

Use a controlled sequence at 30 Hz:

- Frame 20: change texture roots to B.
- Frame 21: load the incoming preset with a two-second soft cut.
- Frame 40: reset textures.
- Inspect frames 19, 20, 40 and 59, plus transition completion.

## Expected distinction

**Without 0010:** subsequent outgoing-shape lookups can pick up B's image, consistent with the new global search paths.

**With 0010:** the outgoing preset continues using A's image while the incoming preset uses B's image. Their appearance changes through the intended transition, rather than redirecting the outgoing lookup.

Keep equations, audio, clock, seeds, dimensions and assets identical between engine roles. Predict exactly which visible object should change incorrectly, when it changes, and why.

Return the proposed preset/assets, host sequence, predicted ownership difference and expected patched appearance. Treat the prediction as a hypothesis to be checked against actual GPU emulator renders.
