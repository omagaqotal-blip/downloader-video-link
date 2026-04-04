#!/usr/bin/env python3
# ytdl.py - YouTube Downloader dengan Menu Interaktif

import os
import sys
import subprocess
import json
import re
import time
import shutil
from pathlib import Path

GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
CYAN = '\033[0;36m'
BLUE = '\033[0;34m'
NC = '\033[0m'

DOWNLOAD_DIR = Path.home() / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def clear():
    os.system('clear')

def print_banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════════╗
║                    YOUTUBE DOWNLOADER                            ║
║                    Support: YouTube, TikTok, Bilibili            ║
╚══════════════════════════════════════════════════════════════╝{NC}
""")

def print_step(step, message):
    icons = {
        'info': f'{CYAN}[i]{NC}',
        'success': f'{GREEN}[✓]{NC}',
        'warning': f'{YELLOW}[!]{NC}',
        'error': f'{RED}[✗]{NC}',
        'download': f'{BLUE}[↓]{NC}'
    }
    print(f"{icons.get(step, '[ ]')} {message}")

def format_size(bytes):
    if bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def format_time(seconds):
    if not seconds or seconds < 0:
        return "--:--"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def check_dependencies():
    print_step('info', 'Memeriksa dependencies...')
    
    missing = []
    
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print_step('success', 'yt-dlp sudah terinstall')
    except:
        print_step('warning', 'yt-dlp tidak ditemukan, menginstall...')
        missing.append('yt-dlp')
    
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print_step('success', 'ffmpeg sudah terinstall')
    except:
        print_step('warning', 'ffmpeg tidak ditemukan, menginstall...')
        missing.append('ffmpeg')
    
    if missing:
        print_step('info', f'Menginstall: {", ".join(missing)}')
        for dep in missing:
            if dep == 'yt-dlp':
                subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            else:
                subprocess.run(['pkg', 'install', dep, '-y'], check=True)
        print_step('success', 'Semua dependencies berhasil diinstall!')
    else:
        print_step('success', 'Semua dependencies sudah tersedia')

def get_video_info(url):
    print_step('info', f'Menganalisis link: {url}')
    
    cmd = [
        'yt-dlp', '-J', '--no-playlist', '--no-warnings',
        '--geo-bypass', url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {'error': f'Gagal menganalisis: {result.stderr[:200]}'}
        
        data = json.loads(result.stdout)
        
        formats = data.get('formats', [])
        title = data.get('title', 'Unknown Title')
        duration = data.get('duration', 0)
        thumbnail = data.get('thumbnail', '')
        
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title).strip('-')[:50]
        
        video_formats = []
        seen = set()
        
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                height = f.get('height', 0)
                fps = f.get('fps') or 0
                
                if height >= 2160:
                    res = '4K'
                elif height >= 1440:
                    res = '2K'
                elif height >= 1080:
                    res = '1080p'
                elif height >= 720:
                    res = '720p'
                elif height >= 480:
                    res = '480p'
                elif height >= 360:
                    res = '360p'
                else:
                    res = f'{height}p'
                
                if fps >= 60:
                    res = f'{res} {fps}fps'
                
                key = f"{height}_{fps}"
                
                if key not in seen:
                    seen.add(key)
                    filesize = f.get('filesize') or f.get('filesize_approx') or 0
                    has_audio = f.get('acodec') != 'none'
                    
                    audio_id = None
                    if not has_audio:
                        for af in formats:
                            if af.get('vcodec') == 'none' and af.get('acodec') != 'none':
                                audio_id = af.get('format_id')
                                break
                    
                    video_formats.append({
                        'id': f.get('format_id'),
                        'resolution': res,
                        'height': height,
                        'fps': fps,
                        'has_audio': has_audio,
                        'filesize': filesize,
                        'filesize_str': format_size(filesize) if filesize > 0 else '?',
                        'audio_id': audio_id
                    })
        
        video_formats.sort(key=lambda x: (x['height'], x['fps']), reverse=True)
        
        audio_formats = []
        seen_audio = set()
        
        for f in formats:
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                abr = f.get('abr') or 0
                if abr < 32:
                    continue
                
                if abr >= 256:
                    quality = '320kbps'
                elif abr >= 192:
                    quality = '256kbps'
                elif abr >= 128:
                    quality = '192kbps'
                elif abr >= 64:
                    quality = '128kbps'
                else:
                    quality = f'{int(abr)}kbps'
                
                if abr not in seen_audio:
                    seen_audio.add(abr)
                    filesize = f.get('filesize') or f.get('filesize_approx') or 0
                    audio_formats.append({
                        'id': f.get('format_id'),
                        'quality': quality,
                        'bitrate': abr,
                        'filesize': filesize,
                        'filesize_str': format_size(filesize) if filesize > 0 else '?'
                    })
        
        audio_formats.sort(key=lambda x: x['bitrate'], reverse=True)
        
        return {
            'title': title,
            'safe_title': safe_title,
            'duration': duration,
            'duration_str': format_time(duration),
            'thumbnail': thumbnail,
            'video_formats': video_formats,
            'audio_formats': audio_formats
        }
        
    except subprocess.TimeoutExpired:
        return {'error': 'Timeout saat menganalisis link'}
    except json.JSONDecodeError:
        return {'error': 'Gagal memproses data dari server'}
    except Exception as e:
        return {'error': str(e)}

def show_menu(info):
    clear()
    print_banner()
    
    print(f"{YELLOW}📹 {info['title'][:60]}{NC}")
    print(f"   Durasi: {info['duration_str']}\n")
    
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}")
    print(f"  {GREEN}PILIH TIPE DOWNLOAD{NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}")
    print(f"  {BLUE}[1]{NC} Video MP4")
    print(f"  {BLUE}[2]{NC} Audio MP3")
    print(f"  {BLUE}[3]{NC} Batal\n")
    
    return input(f"{YELLOW}Pilihan Anda (1-3): {NC}").strip()

def show_video_menu(formats):
    clear()
    print_banner()
    
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}")
    print(f"  {GREEN}PILIH RESOLUSI VIDEO{NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}\n")
    
    for i, fmt in enumerate(formats, 1):
        audio_status = "✓ Audio" if fmt['has_audio'] else "✗ No Audio"
        print(f"  {BLUE}[{i}]{NC} {fmt['resolution']:<12} {audio_status:<10} {fmt['filesize_str']}")
    
    print(f"\n  {BLUE}[0]{NC} Kembali")
    print(f"  {BLUE}[q]{NC} Batal\n")
    
    return input(f"{YELLOW}Pilih resolusi (1-{len(formats)}): {NC}").strip()

def show_audio_menu(formats):
    clear()
    print_banner()
    
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}")
    print(f"  {GREEN}PILIH KUALITAS AUDIO{NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════════{NC}\n")
    
    for i, fmt in enumerate(formats, 1):
        print(f"  {BLUE}[{i}]{NC} {fmt['quality']:<12} {fmt['filesize_str']}")
    
    print(f"\n  {BLUE}[0]{NC} Kembali")
    print(f"  {BLUE}[q]{NC} Batal\n")
    
    return input(f"{YELLOW}Pilih kualitas (1-{len(formats)}): {NC}").strip()

def download_video(url, format_id, audio_id, title, resolution):
    filename = f"{title}-{resolution}.mp4"
    filepath = DOWNLOAD_DIR / filename
    
    counter = 1
    while filepath.exists():
        filename = f"{title}-{resolution}-{counter}.mp4"
        filepath = DOWNLOAD_DIR / filename
        counter += 1
    
    print_step('download', f'Mulai download: {resolution}')
    print_step('info', f'Judul: {title}')
    print_step('info', f'Lokasi: {filepath}\n')
    
    if audio_id:
        format_spec = f"{format_id}+{audio_id}"
    else:
        format_spec = format_id
    
    cmd = [
        'yt-dlp', '-f', format_spec, '--merge-output-format', 'mp4',
        '-o', str(filepath), '--no-playlist', '--progress', '--no-warnings',
        '--geo-bypass', url
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        for line in process.stdout:
            if '%' in line:
                percent_match = re.search(r'(\d+\.?\d*)%', line)
                if percent_match:
                    progress = float(percent_match.group(1))
                    bar_len = 30
                    filled = int(bar_len * progress / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    
                    speed_match = re.search(r'at\s+([\d\.]+\w+/s)', line)
                    speed = speed_match.group(1) if speed_match else ''
                    
                    eta_match = re.search(r'ETA\s+(\d{2}:\d{2})', line)
                    eta = eta_match.group(1) if eta_match else ''
                    
                    sys.stdout.write(f'\r  [{bar}] {progress:.1f}%  {speed}  ETA: {eta}    ')
                    sys.stdout.flush()
        
        process.wait()
        sys.stdout.write('\n\n')
        
        if process.returncode == 0 and filepath.exists():
            size = format_size(filepath.stat().st_size)
            print_step('success', f'Download selesai!')
            print_step('info', f'File: {filepath.name}')
            print_step('info', f'Ukuran: {size}')
            return True
        else:
            print_step('error', 'Download gagal!')
            return False
            
    except Exception as e:
        print_step('error', f'Error: {e}')
        return False

def download_audio(url, format_id, title, quality):
    filename = f"{title}-{quality}.mp3"
    filepath = DOWNLOAD_DIR / filename
    
    counter = 1
    while filepath.exists():
        filename = f"{title}-{quality}-{counter}.mp3"
        filepath = DOWNLOAD_DIR / filename
        counter += 1
    
    print_step('download', f'Mulai download audio: {quality}')
    print_step('info', f'Judul: {title}')
    print_step('info', f'Lokasi: {filepath}\n')
    
    cmd = [
        'yt-dlp', '-f', format_id, '-x', '--audio-format', 'mp3',
        '-o', str(filepath), '--no-playlist', '--progress', '--no-warnings',
        '--geo-bypass', url
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        for line in process.stdout:
            if '%' in line:
                percent_match = re.search(r'(\d+\.?\d*)%', line)
                if percent_match:
                    progress = float(percent_match.group(1))
                    bar_len = 30
                    filled = int(bar_len * progress / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    
                    sys.stdout.write(f'\r  [{bar}] {progress:.1f}%    ')
                    sys.stdout.flush()
        
        process.wait()
        sys.stdout.write('\n\n')
        
        if process.returncode == 0 and filepath.exists():
            size = format_size(filepath.stat().st_size)
            print_step('success', f'Download selesai!')
            print_step('info', f'File: {filepath.name}')
            print_step('info', f'Ukuran: {size}')
            return True
        else:
            print_step('error', 'Download gagal!')
            return False
            
    except Exception as e:
        print_step('error', f'Error: {e}')
        return False

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        clear()
        print_banner()
        url = input(f"{YELLOW}Masukkan YouTube URL: {NC}").strip()
    
    if not url:
        print_step('error', 'URL tidak boleh kosong!')
        sys.exit(1)
    
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    
    clear()
    print_banner()
    
    check_dependencies()
    print()
    
    info = get_video_info(url)
    
    if 'error' in info:
        print_step('error', info['error'])
        sys.exit(1)
    
    while True:
        choice = show_menu(info)
        
        if choice == '1':
            while True:
                video_choice = show_video_menu(info['video_formats'])
                
                if video_choice == '0':
                    break
                elif video_choice.lower() == 'q':
                    print_step('info', 'Download dibatalkan')
                    return
                
                try:
                    idx = int(video_choice) - 1
                    if 0 <= idx < len(info['video_formats']):
                        selected = info['video_formats'][idx]
                        success = download_video(
                            url,
                            selected['id'],
                            selected.get('audio_id'),
                            info['safe_title'],
                            selected['resolution'].replace(' ', '')
                        )
                        if success:
                            print()
                            input(f"{YELLOW}Tekan Enter untuk kembali...{NC}")
                        return
                    else:
                        print_step('error', 'Pilihan tidak valid!')
                        time.sleep(1)
                except ValueError:
                    print_step('error', 'Masukkan angka yang valid!')
                    time.sleep(1)
        
        elif choice == '2':
            if not info['audio_formats']:
                print_step('error', 'Tidak ada format audio yang tersedia!')
                time.sleep(2)
                continue
            
            while True:
                audio_choice = show_audio_menu(info['audio_formats'])
                
                if audio_choice == '0':
                    break
                elif audio_choice.lower() == 'q':
                    print_step('info', 'Download dibatalkan')
                    return
                
                try:
                    idx = int(audio_choice) - 1
                    if 0 <= idx < len(info['audio_formats']):
                        selected = info['audio_formats'][idx]
                        success = download_audio(
                            url,
                            selected['id'],
                            info['safe_title'],
                            selected['quality']
                        )
                        if success:
                            print()
                            input(f"{YELLOW}Tekan Enter untuk kembali...{NC}")
                        return
                    else:
                        print_step('error', 'Pilihan tidak valid!')
                        time.sleep(1)
                except ValueError:
                    print_step('error', 'Masukkan angka yang valid!')
                    time.sleep(1)
        
        elif choice == '3' or choice.lower() == 'q':
            print_step('info', 'Download dibatalkan')
            return
        
        else:
            print_step('error', 'Pilihan tidak valid!')
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[!] Download dibatalkan oleh user{NC}")
        sys.exit(0)
