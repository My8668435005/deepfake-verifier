"""Central configuration. Change weights / thresholds here, nowhere else."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
ARTIFACT_DIR = DATA_DIR / "artifacts"
REPORT_DIR = DATA_DIR / "reports"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(DATA_DIR / 'app.db').as_posix()}")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "100"))

ALLOWED_EXTENSIONS = {
    "IMAGE": [".jpg", ".jpeg", ".png", ".webp"],
    "VIDEO": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "AUDIO": [".wav", ".mp3", ".flac", ".m4a", ".ogg"],
}

# ---- score fusion -----------------------------------------------------------
# Weight GROUPS (from the project overview). Re-normalised when a group is missing.
FUSION_WEIGHTS = {"ml": 0.50, "forensics": 0.25, "metadata": 0.15, "audio": 0.10}

# Every module's `name` must be a key here. None = evidence only (not scored).
MODULE_WEIGHT_GROUP = {
    "image_ml": "ml",
    "video_ml": "ml",
    "forensics": "forensics",
    "metadata": "metadata",
    "audio": "audio",
    "ocr": None,
}

# score <  AUTHENTIC_MAX            -> Likely Authentic
# AUTHENTIC_MAX <= score < FAKE_MIN -> Suspicious
# score >= FAKE_MIN                 -> Likely Fake
AUTHENTIC_MAX = 0.35
FAKE_MIN = 0.65
