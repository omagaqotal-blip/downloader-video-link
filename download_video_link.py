#!/usr/bin/env python3
# YouTube Video Downloader for Termux

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check and install required dependencies"""
    dependencies = {
        'yt-dlp': 'yt-dlp',
        'ffmpeg': 'ffmpeg'
    }
    
    missing = []
    for dep, package in dependencies.items():
        result = subprocess.run(['which', dep], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(package)
    
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)}")
        for package in missing:
            subprocess.run(['pkg', 'install', package, '-y'], check=True)
        print("Dependencies installed successfully!")
    else:
        print("All dependencies are already installed")

def download_video(url, output_path=None, quality='best'):
    """Download video from YouTube"""
    
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    quality_map = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'audio': 'bestaudio/best'
    }
    
    format_spec = quality_map.get(quality, quality_map['best'])
    
    cmd = [
        'yt-dlp',
        '-f', format_spec,
        '--merge-output-format', 'mp4' if quality != 'audio' else 'mp3',
        '-o', f'{output_path}/%(title)s.%(ext)s',
        '--no-playlist',
        '--progress',
        url
    ]
    
    if quality == 'audio':
        cmd.extend(['-x', '--audio-format', 'mp3'])
    
    try:
        print(f"Downloading from: {url}")
        print(f"Quality: {quality}")
        print(f"Saving to: {output_path}")
        subprocess.run(cmd, check=True)
        print("Download completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e}")
        return False

def download_playlist(url, output_path=None, quality='best', max_count=None):
    """Download YouTube playlist"""
    
    if output_path is None:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    cmd = [
        'yt-dlp',
        '-f', 'bestvideo+bestaudio/best',
        '--merge-output-format', 'mp4',
        '-o', f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s',
        '--yes-playlist',
        '--progress'
    ]
    
    if max_count:
        cmd.extend(['--playlist-end', str(max_count)])
    
    cmd.append(url)
    
    try:
        print(f"Downloading playlist from: {url}")
        subprocess.run(cmd, check=True)
        print("Playlist download completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Playlist download failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='YouTube Video Downloader for Termux')
    parser.add_argument('url', help='YouTube video or playlist URL')
    parser.add_argument('-q', '--quality', choices=['best', '1080p', '720p', '480p', 'audio'], 
                       default='best', help='Video quality (default: best)')
    parser.add_argument('-o', '--output', help='Output directory (default: ./downloads)')
    parser.add_argument('-p', '--playlist', action='store_true', help='Download as playlist')
    parser.add_argument('-m', '--max', type=int, help='Maximum videos to download from playlist')
    parser.add_argument('--setup', action='store_true', help='Install dependencies only')
    
    args = parser.parse_args()
    
    if args.setup:
        check_dependencies()
        return
    
    if not args.url:
        print("Error: URL is required")
        parser.print_help()
        sys.exit(1)
    
    check_dependencies()
    
    if args.playlist:
        download_playlist(args.url, args.output, args.quality, args.max)
    else:
        download_video(args.url, args.output, args.quality)

if __name__ == "__main__":
    main()
