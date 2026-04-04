#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
from pathlib import Path

def check_dependencies():
    missing = []
    for dep in ['yt-dlp', 'ffmpeg']:
        result = subprocess.run(['which', dep], capture_output=True, text=True)
        if result.returncode != 0:
            missing.append(dep)
    
    if missing:
        print(f"Installing: {', '.join(missing)}")
        for dep in missing:
            if dep == 'yt-dlp':
                subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            else:
                subprocess.run(['pkg', 'install', dep, '-y'], check=True)
        print("Dependencies installed!")

def get_video_info(url):
    cmd = ['yt-dlp', '--dump-json', '--no-playlist', url]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def download_video(url, quality='best', output_dir='downloads'):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    quality_map = {
        'best': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        'audio': 'bestaudio/best'
    }
    
    format_spec = quality_map.get(quality, quality_map['best'])
    
    cmd = ['yt-dlp', '-f', format_spec, '--merge-output-format', 'mp4',
           '-o', f'{output_dir}/%(title)s.%(ext)s', '--no-playlist', '--progress', url]
    
    if quality == 'audio':
        cmd = ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', f'{output_dir}/%(title)s.%(ext)s', url]
    
    print(f"\nDownloading: {url}")
    print(f"Quality: {quality}")
    print(f"Output: {output_dir}\n")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Download completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Failed: {e}")
        return False

def interactive_mode():
    print("\n" + "="*50)
    print("YOUTUBE DOWNLOADER FOR TERMUX")
    print("="*50)
    
    url = input("\nEnter YouTube URL: ").strip()
    if not url:
        print("URL required!")
        return
    
    print("\nQuality options:")
    print("1. Best quality")
    print("2. 1080p")
    print("3. 720p")
    print("4. 480p")
    print("5. 360p")
    print("6. Audio only (MP3)")
    
    choice = input("\nChoose (1-6): ").strip()
    
    quality_map = {
        '1': 'best', '2': '1080p', '3': '720p',
        '4': '480p', '5': '360p', '6': 'audio'
    }
    
    quality = quality_map.get(choice, 'best')
    
    output_dir = input("Output directory [downloads]: ").strip()
    if not output_dir:
        output_dir = 'downloads'
    
    download_video(url, quality, output_dir)

def main():
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    parser = argparse.ArgumentParser(description='YouTube Downloader')
    parser.add_argument('url', nargs='?', help='YouTube URL')
    parser.add_argument('-q', '--quality', choices=['best', '1080p', '720p', '480p', '360p', 'audio'], 
                       default='best', help='Video quality')
    parser.add_argument('-o', '--output', default='downloads', help='Output directory')
    parser.add_argument('--setup', action='store_true', help='Install dependencies')
    
    args = parser.parse_args()
    
    if args.setup:
        check_dependencies()
        return
    
    if not args.url:
        print("Error: URL required")
        sys.exit(1)
    
    check_dependencies()
    download_video(args.url, args.quality, args.output)

if __name__ == "__main__":
    main()
