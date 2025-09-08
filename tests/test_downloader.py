"""Tests for the downloader module."""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from downloader.core.downloader import round_down_to_nearest_half_hour, create_urls


def test_round_down_to_nearest_half_hour():
    """Test that times are properly rounded down to the nearest half hour."""
    # Test exact half hour
    dt = datetime(2024, 9, 6, 18, 30, 0)
    result = round_down_to_nearest_half_hour(dt)
    assert result == datetime(2024, 9, 6, 18, 30, 0)

    # Test time that needs rounding
    dt = datetime(2024, 9, 6, 18, 45, 30)
    result = round_down_to_nearest_half_hour(dt)
    assert result == datetime(2024, 9, 6, 18, 30, 0)

    # Test time at the hour
    dt = datetime(2024, 9, 6, 19, 0, 0)
    result = round_down_to_nearest_half_hour(dt)
    assert result == datetime(2024, 9, 6, 19, 0, 0)


def test_create_urls():
    """Test URL creation for video segments."""
    import os

    # Mock the environment variable
    os.environ["HOST_URL"] = "https://example.com"

    rink = 153
    start_date = datetime(2024, 9, 6, 18, 30, 0)
    length = timedelta(hours=1)

    urls = create_urls(rink, start_date, length)

    # Should create URLs for the segments needed
    assert len(urls) >= 2  # At least 2 30-minute segments for 1 hour
    assert "153" in urls[0]
    assert "2024-09-06" in urls[0]
    assert "18:30" in urls[0]
