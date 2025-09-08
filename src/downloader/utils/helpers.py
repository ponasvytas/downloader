"""Utility functions and helpers for the downloader package."""

from pathlib import Path
from typing import List
import os


def ensure_directory_exists(directory: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    directory.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the root directory of the project."""
    return Path(__file__).parent.parent.parent.parent


def get_video_directory(team_name: str) -> Path:
    """Get the video directory for a specific team."""
    return get_project_root() / "video" / team_name


def validate_environment_variables() -> bool:
    """Check if required environment variables are set."""
    required_vars = ["HOST_URL", "DOWNLOADER_USERNAME", "DOWNLOADER_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these variables.")
        return False

    return True


def get_mp4_files(directory: Path) -> List[Path]:
    """Get all MP4 files in a directory, sorted by name."""
    if not directory.exists():
        return []

    return sorted(list(directory.glob("part*.mp4")))
