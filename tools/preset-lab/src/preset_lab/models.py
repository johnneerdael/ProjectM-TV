from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PresetRecord:
    path: str
    sha256: str
    weight_mb: int


@dataclass(frozen=True, slots=True)
class EngineIdentity:
    commit: str
    patches_sha256: str
    instrumentation_sha256: str


@dataclass(frozen=True, slots=True)
class RunConfig:
    width: int = 256
    height: int = 144
    fps: int = 30
    warmup_seconds: float = 4
    measurement_seconds: float = 20
    seed: int = 12345
    audio_path: str = "controlled-pcm"


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    repo: Path
    audio_root: Path
    work: Path
    audience_config: Path | None = None
    run: RunConfig = RunConfig()
    concurrency: int = 1
    timeout_seconds: float = 120
    preset_limit: int | None = None
    corpus_manifest: Path | None = None


@dataclass(frozen=True, slots=True)
class JobSpec:
    preset: PresetRecord
    stimulus_id: str
    pcm_path: Path
    config: RunConfig
    identity: EngineIdentity
    preset_root: Path
    texture_root: Path
    work: Path


@dataclass(frozen=True, slots=True)
class WorkerResult:
    status: str
    manifest: dict
    diagnostics_path: Path


@dataclass(frozen=True, slots=True)
class StaticEvidence:
    complete: bool
    paths: list[dict]
    unsupported: list[str]


@dataclass(frozen=True, slots=True)
class Fingerprint:
    preset: PresetRecord
    raw: dict
    normalized: dict
    quality: dict
    evidence: dict


@dataclass(frozen=True, slots=True)
class TrackRecord:
    id: str
    path: Path
    genre_ids: tuple[str, ...]
    sha256: str
    duration: float
    excerpts: tuple[tuple[float, float], ...]


@dataclass(frozen=True, slots=True)
class Corpus:
    tracks: tuple[TrackRecord, ...]
    descriptors: dict
    identity: str


@dataclass(frozen=True, slots=True)
class MatchDecision:
    preset: PresetRecord
    genre_id: str
    music_fit: float
    audience_fit: float
    score: float
    included: bool
    evidence_state: str
    contributions: dict


@dataclass(frozen=True, slots=True)
class PipelineResult:
    render_jobs: int
    reused_jobs: int
    failed_jobs: int
    export_path: Path | None
