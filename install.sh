#!/bin/bash
echo "Installing YouTube Downloader..."
pkg update -y
pkg install python ffmpeg -y
pip install yt-dlp
curl -O https://raw.githubusercontent.com/omagaqotal-blip/youtube-downloader/main/yt_downloader.py
chmod +x yt_downloader.py
echo ""
echo "Installation complete!"
echo "Run: python yt_downloader.py"
