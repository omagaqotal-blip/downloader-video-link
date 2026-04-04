#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_deps():
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except:
        print("Installing yt-dlp...")
        subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except:
        print("Installing ffmpeg...")
        subprocess.run(['pkg', 'install', 'ffmpeg', '-y'], check=True)

def download(url, quality='best', output='downloads'):
    Path(output).mkdir(parents=True, exist_ok=True)
    
    qmap = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'audio': 'bestaudio/best'
    }
    
    fmt = qmap.get(quality, qmap['best'])
    
    cmd = ['yt-dlp', '-f', fmt, '--merge-output-format', 'mp4',
           '-o', f'{output}/%(title)s.%(ext)s', '--progress', url]
    
    if quality == 'audio':
        cmd = ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', f'{output}/%(title)s.%(ext)s', url]
    
    print(f"Downloading: {url}")
    subprocess.run(cmd, check=True)
    print("Done!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='YouTube URL')
    parser.add_argument('-q', '--quality', default='best', 
                       choices=['best', '1080p', '720p', '480p', 'audio'])
    parser.add_argument('-o', '--output', default='downloads')
    args = parser.parse_args()
    
    check_deps()
    download(args.url, args.quality, args.output)

if __name__ == "__main__":
    main()
