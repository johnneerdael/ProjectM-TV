"""Build capture-only variants from frozen engine snapshots; never edit engine code."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import preset_lab.build_worker as builder

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
REPO = EVIDENCE.parents[3]
SCRATCH = REPO / "build/diffusion/corpus-screen"


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    native = SCRATCH / "sparse-native"
    shutil.copytree(builder.NATIVE, native, dirs_exist_ok=True)
    cmake = native / "CMakeLists.txt"
    cmake.write_text(replace(cmake.read_text(), 'add_subdirectory("${PROJECTM_SOURCE}" projectm)',
                            'add_compile_definitions(MILKDROP_PRESET_DEBUG)\n'
                            'add_subdirectory("${PROJECTM_SOURCE}" projectm)'))
    path = native / "worker.cpp"
    text = path.read_text()
    text = replace(text, "        int block = 44100 / fps;", """        std::vector<int> capture_indices;
        if (job.contains("capture_frame_indices")) {
            capture_indices = job.at("capture_frame_indices").get<std::vector<int>>();
            if (capture_indices.empty()) throw std::runtime_error("empty capture selection");
            int previous = -1;
            for (int index : capture_indices) {
                if (index <= previous || index >= frames)
                    throw std::runtime_error("invalid capture selection");
                previous = index;
            }
        } else {
            for (int frame = 0; frame < frames; ++frame) capture_indices.push_back(frame);
        }
        size_t captured = 0;
        int block = 44100 / fps;""")
    text = replace(text, "            auto pixels = capture.Read();", """            const bool selected = captured < capture_indices.size() && capture_indices[captured] == frame;
            std::vector<unsigned char> pixels;
            if (selected) pixels = capture.Read();""")
    text = replace(text, """            std::cout.write(reinterpret_cast<char*>(pixels.data()), pixels.size());
            if (!std::cout) throw std::runtime_error("frame consumer closed");""", """            if (selected) {
                std::cout.write(reinterpret_cast<char*>(pixels.data()), pixels.size());
                if (!std::cout) throw std::runtime_error("frame consumer closed");
                ++captured;
            }""")
    text = replace(text, '                       {"width", width}, {"height", height}, {"fps", fps},',
                   '                       {"captured_frames", captured}, {"capture_frame_indices", capture_indices},\n'
                   '                       {"capture_protocol", "sparse-v1"},\n'
                   '                       {"width", width}, {"height", height}, {"fps", fps},')
    path.write_text(text)
    native_digest = hashlib.sha256()
    for file in sorted(native.rglob("*")):
        if file.is_file():
            native_digest.update(file.relative_to(native).as_posix().encode())
            native_digest.update(file.read_bytes())
    result = {"capture_protocol": "sparse-v1", "native_sources_sha256": native_digest.hexdigest(),
              "diagnostic_compile_definition": "MILKDROP_PRESET_DEBUG",
              "capture_frame_indices": [120, 150, 180, 210, 239, 300, 390, 479], "workers": {}}
    for label in ["baseline", "reviewed"]:
        frozen = json.loads((EVIDENCE / f"worker-{label}.json").read_text())
        output = SCRATCH / f"sparse-build-{label}"
        output.mkdir(parents=True, exist_ok=True)
        with (output / "build.log").open("w") as log:
            subprocess.run(["cmake", "-S", str(native), "-B", str(output),
                            f'-DPROJECTM_SOURCE={frozen["snapshot"]}', "-DCMAKE_BUILD_TYPE=Release"],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
            subprocess.run(["cmake", "--build", str(output), "-j", "4"], check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        executable = output / "preset-lab-worker"
        result["workers"][label] = {"exe": str(executable), "snapshot": frozen["snapshot"],
                                    "identity": frozen["identity"],
                                    "worker_sha256": hashlib.sha256(executable.read_bytes()).hexdigest()}
        print(label, "sparse worker built", flush=True)
    (HERE / "sparse-workers.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
