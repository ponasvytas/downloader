"""Tests for the concatenator module."""

import cv2
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from downloader.core.concatenator import read_video_details, update_details
from downloader.models.settings import VideoDetails


@patch("downloader.core.concatenator.cv2.VideoCapture")
def test_read_video_details(mock_video_capture):
    """Test reading video details from a file."""
    # Mock the video capture object
    mock_cap = Mock()
    mock_cap.get.side_effect = lambda prop: {
        cv2.CAP_PROP_FPS: 30.0,
        cv2.CAP_PROP_FRAME_HEIGHT: 1080,
        cv2.CAP_PROP_FRAME_WIDTH: 1920,
        cv2.CAP_PROP_FRAME_COUNT: 108000,  # 3600 seconds at 30fps
    }[prop]

    mock_video_capture.return_value = mock_cap

    # Test the function
    test_path = Path("test_video.mp4")
    result = read_video_details(test_path)

    assert result.frame_rate == 30.0
    assert result.height == 1080
    assert result.width == 1920
    assert result.length == 3600.0  # 108000 / 30

    # Verify cv2.VideoCapture was called with the correct path
    mock_video_capture.assert_called_once_with(str(test_path))


@patch("downloader.core.concatenator.cv2.VideoCapture")
def test_read_video_details_different_fps(mock_video_capture):
    """Test reading video details with different frame rate."""
    mock_cap = Mock()
    mock_cap.get.side_effect = lambda prop: {
        cv2.CAP_PROP_FPS: 24.0,
        cv2.CAP_PROP_FRAME_HEIGHT: 720,
        cv2.CAP_PROP_FRAME_WIDTH: 1280,
        cv2.CAP_PROP_FRAME_COUNT: 72000,  # 3000 seconds at 24fps
    }[prop]

    mock_video_capture.return_value = mock_cap

    result = read_video_details(Path("test.mp4"))

    assert result.frame_rate == 24.0
    assert result.height == 720
    assert result.width == 1280
    assert result.length == 3000.0  # 72000 / 24


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"videoName": "test", "rinkCode": 123}',
)
@patch("downloader.core.concatenator.GameInfo")
def test_update_details(mock_game_info, mock_file):
    """Test updating video details in JSON file."""
    # Setup mock GameInfo instance
    mock_game_info_instance = Mock()
    mock_game_info.return_value = mock_game_info_instance
    mock_game_info_instance.model_dump_json.return_value = '{"updated": "data"}'

    # Create test data
    test_details = VideoDetails(frame_rate=30.0, height=1080, width=1920, length=3600.0)
    test_path = Path("test_info.json")

    # Call the function
    update_details(test_path, test_details)

    # Verify file operations
    mock_file.assert_called()
    mock_game_info_instance.model_dump_json.assert_called_once_with(
        by_alias=True, indent=2
    )
