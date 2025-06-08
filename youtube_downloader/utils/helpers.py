import os
import re
from pathlib import Path

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", title)

def get_default_download_dir():
    """Get default download directory (Downloads folder)"""
    return str(Path.home() / "Downloads")

def ensure_dir_exists(directory):
    """Ensure directory exists, create if not"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def get_available_resolutions():
    """Return list of common YouTube resolutions"""
    return ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]

def get_audio_formats():
    """Return list of supported audio formats"""
    return ["mp3", "flac"]