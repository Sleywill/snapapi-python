"""
Video recording example.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/video_recording.py
"""

import os

from snapapi import SnapAPI

with SnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
    video_data = snap.video(
        url="https://example.com",
        format="mp4",
        duration=10,
        width=1280,
        height=720,
        fps=30,
        scrolling=True,
        scroll_speed=200,
        dark_mode=True,
        block_ads=True,
        block_cookie_banners=True,
    )
    with open("recording.mp4", "wb") as f:
        f.write(video_data)
    print(f"Saved recording.mp4 ({len(video_data)} bytes)")
