#!/bin/bash
if [ -z "$1" ]; then
    python yt_downloader.py
else
    python yt_downloader.py "$1"
fi
