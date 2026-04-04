#!/bin/bash
echo "Installing YouTube Downloader..."
pkg update -y
pkg install python ffmpeg -y
pip install yt-dlp
curl -O https://raw.githubusercontent.com/omagaqotal-blip/downloader-video-link/main/download_video_link.py
chmod +x download_video_link.py
echo ""
echo "Installation complete!"
echo "Run: python download_video_link.py"
