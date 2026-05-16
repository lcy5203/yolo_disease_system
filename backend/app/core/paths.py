from pathlib import Path
import os
import sys


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root() -> Path:
    """Directory that contains bundled read-only resources."""
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[2]


def runtime_root() -> Path:
    """Directory for writable runtime files such as sqlite DB and uploads."""
    env_root = os.getenv("YOLO_DISEASE_HOME")
    if env_root:
        return Path(env_root).expanduser().resolve()
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return bundle_root()


def resource_path(relative_path: str) -> Path:
    runtime_candidate = runtime_root() / relative_path
    if runtime_candidate.exists():
        return runtime_candidate
    return bundle_root() / relative_path


def runtime_path(relative_path: str) -> Path:
    path = runtime_root() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
