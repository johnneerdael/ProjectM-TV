"""Build a private P1/raw-point experiment from the overwrite-fix snapshot."""
import difflib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PROVIDER = ROOT / 'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py'
spec = importlib.util.spec_from_file_location('shared_core_builder', PROVIDER)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.WORK = ROOT / 'build/native-4k-current-main/raw-point-experiment'
b.WORK.mkdir(parents=True, exist_ok=True)
original_prepare = b.prepare
ADAPTER = Path(__file__).resolve()


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise ValueError(f'{label}: expected one source match, found {text.count(old)}')
    return text.replace(old, new)


def diff(before, after, name, production=False):
    return ''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True),
        fromfile=('production/' if production else 'a/') + name,
        tofile=('diagnostic/' if production else 'b/') + name))


def prepare(variant, commit):
    destination, source, identity = original_prepare(variant, commit)
    engine = source / 'third_party/projectm'
    patch = source / 'tools/projectm-patches/0030-feedback-diffusion-compensation.patch'
    names = ['src/libprojectM/MilkdropPreset/' + name for name in
             ('MilkdropPreset.cpp', 'PresetState.hpp', 'MilkdropShader.cpp')]
    before = {name: (engine / name).read_text() for name in names}
    original_patch = patch.read_text()
    (destination / 'production-0030.patch').write_text(original_patch)
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(source))
    # Recover the exact prerequisite text for the overlapping production hunk.
    subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=engine, env=env, check=True)
    prerequisite_preset = (engine / names[0]).read_text()
    subprocess.run(['git', 'apply', str(patch)], cwd=engine, env=env, check=True)
    if any((engine / name).read_text() != before[name] for name in names):
        raise ValueError('production patch round trip changed instrumented source')

    preset = replace_once(before[names[0]],
        'const bool diffuseAtOutput = m_feedbackDiffusion.Active() && !motionVectorsDrawn;',
        'const bool diffuseAtOutput = false;', 'P1 placement')
    original_else = '''    else
    {
        if (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame)
        {
            m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
        }
        m_state.mainTexture = m_flipTexture.Texture();
    }
    m_flipHoldsPreviousFrame = false;'''
    replacement_else = '''    else
    {
        m_state.mainTexture = m_flipTexture.Texture();
    }
    m_flipHoldsPreviousFrame = false;'''
    preset = replace_once(preset, original_else, replacement_else, 'reuse raw flip')
    active_start = '''    if (m_feedbackDiffusion.Active())
    {
        // P2 reuses the previous end-of-frame result.'''
    raw_start = '''    // Private diagnostic: retain raw point feedback separately from filtered bilinear input.
    // Reuse the previous final flip unless the raw canvas changed; no per-frame allocation.
    if (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame)
    {
        m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
    }
    m_state.rawPointFeedbackTexture = m_flipTexture.Texture();

    if (m_feedbackDiffusion.Active())
    {
        // P2 reuses the previous end-of-frame result.'''
    preset = replace_once(preset, active_start, raw_start, 'raw previous flip')

    state = replace_once(before[names[1]],
        '    std::weak_ptr<Renderer::Texture> mainTexture; //!< A weak reference to the main texture in the preset framebuffer.',
        '    std::weak_ptr<Renderer::Texture> mainTexture; //!< A weak reference to the main texture in the preset framebuffer.\n'
        '    std::weak_ptr<Renderer::Texture> rawPointFeedbackTexture; //!< Private diagnostic: raw y-flipped previous canvas.',
        'raw weak texture')

    shader = replace_once(before[names[2]],
        '''        // Update main texture, swaps every frame.
        desc.Texture(presetState.mainTexture);
        desc.Bind(textureUnit, m_shader);''',
        '''        // Private diagnostic: only warp point samplers bypass feedback diffusion.
        const auto sampler = desc.Sampler();
        const bool rawPoint = m_type == ShaderType::WarpShader && sampler &&
                              sampler->FilterMode() == GL_NEAREST &&
                              !presetState.rawPointFeedbackTexture.expired();
        desc.Texture(rawPoint ? presetState.rawPointFeedbackTexture : presetState.mainTexture);
        desc.Bind(textureUnit, m_shader);''',
        'sampler-based warp routing')
    after = dict(zip(names, (preset, state, shader)))
    for name in names:
        (engine / name).write_text(after[name])

    # Replace the overlapping production cpp section, then append the two new private hunks.
    marker = 'diff --git a/' + names[0] + ' b/' + names[0] + '\n'
    start = original_patch.index(marker)
    end = original_patch.index('\ndiff --git ', start + len(marker)) + 1
    copied_patch = original_patch[:start] + marker + diff(prerequisite_preset, preset, names[0]) + original_patch[end:]
    for name in names[1:]:
        copied_patch += 'diff --git a/' + name + ' b/' + name + '\n' + diff(before[name], after[name], name)
    patch.write_text(copied_patch)
    subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=engine, env=env, check=True)

    private_diff = destination / 'raw-point-private.diff'
    private_diff.write_text(''.join(diff(before[name], after[name], name, True) for name in names))
    identity['ordered_patches'][-1]['sha256'] = b.sha(patch)
    identity['source_patch_sha256'] = b.digest([(p['name'], p['sha256']) for p in identity['ordered_patches']])
    identity['private_raw_point_experiment'] = {
        'placement': 'P1 always; raw final composite',
        'routing': 'WarpShader main descriptors with actual Sampler::FilterMode()==GL_NEAREST use raw previous flip; all others retain mainTexture',
        'raw_flip_lifetime': 'existing CopyTexture framebuffer; reused from previous final flip; refresh after first frame, resize, invalidation or motion-vector drawing',
        'blur_source_and_timing': 'unchanged production raw previous framebuffer and existing timing',
        'shipping_byte_identity': False,
        'production_source_commit': commit,
        'adapter_sha256': b.sha(ADAPTER),
        'private_diff_sha256': b.sha(private_diff),
        'production_patch_sha256': b.sha(destination / 'production-0030.patch'),
        'diagnostic_patch_sha256': b.sha(patch),
        'reverse_patch_check': 'passed against adapted instrumented source',
        'altered_source_sha256': {name: {'before': b.digest(before[name]), 'after_file': b.sha(engine / name)} for name in names},
    }
    # Before hashes are byte hashes, like after hashes, rather than JSON string digests.
    for name in names:
        identity['private_raw_point_experiment']['altered_source_sha256'][name]['before'] = b.hashlib.sha256(before[name].encode()).hexdigest()
    (source / 'corpus-app/src/main/assets/backend-identity.json').write_text(b.canonical(identity) + '\n')
    (destination / 'identity.json').write_text(b.canonical(identity) + '\n')
    return destination, source, identity


if __name__ == '__main__':
    b.prepare = prepare
    commit = subprocess.check_output(['git', 'rev-parse', '790aaa24'], cwd=ROOT, text=True).strip()
    b.build('candidate', commit)
    metadata_path = b.WORK / 'worker-candidate.json'
    metadata = json.loads(metadata_path.read_text())
    destination = Path(metadata['apk']).parent
    source = destination / 'repo'
    with (destination / 'core-aar.log').open('w') as log:
        b.run([str(source / 'gradlew'), '--no-daemon', ':core:bundleReleaseAar'], source, log)
    aar = source / 'core/build/outputs/aar/core-release.aar'
    with zipfile.ZipFile(aar) as archive:
        core_sha = b.hashlib.sha256(archive.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest()
    if core_sha != metadata['backend_identity']['core_sha256']:
        raise ValueError('actual core AAR ELF differs from diagnostic APK ELF')
    metadata['actual_core_aar'] = {'path': str(aar), 'sha256': b.sha(aar), 'core_sha256': core_sha, 'apk_elf_identity': True}
    metadata_path.write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({'metadata': str(metadata_path), 'apk_sha256': metadata['apk_sha256'], 'actual_core_aar': metadata['actual_core_aar']}))
