from pytubefix import YouTube
from pytubefix import YouTube as PyTube
import yt_dlp
from moviepy.editor import VideoFileClip
import os
import re

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_with_pytubefix(link, output_path=None, resolution=None, progress_callback=None):
    """Download video using pytubefix library"""
    try:
        yt = YouTube(link)
        if progress_callback:
            progress_callback(f"Title: {yt.title}")
            progress_callback(f"Length: {yt.length} seconds")
        
        if resolution:
            stream = yt.streams.filter(res=resolution).first()
            if not stream:
                if progress_callback:
                    progress_callback(f"Resolution {resolution} not available. Getting highest resolution...")
                stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_highest_resolution()
            
        if progress_callback:
            progress_callback(f"Downloading: {stream.resolution}")
        
        if output_path:
            video_path = stream.download(output_path=output_path)
        else:
            video_path = stream.download()
            
        if progress_callback:
            progress_callback("Download completed with pytubefix!")
        return video_path
    except Exception as e:
        if progress_callback:
            progress_callback(f"pytubefix download failed: {e}")
        return None

def download_with_pytube(link, output_path=None, resolution=None, progress_callback=None):
    """Download video using standard pytube library"""
    try:
        yt = PyTube(link)
        if progress_callback:
            progress_callback(f"Title: {yt.title}")
            progress_callback(f"Length: {yt.length} seconds")
        
        if resolution:
            stream = yt.streams.filter(res=resolution).first()
            if not stream:
                if progress_callback:
                    progress_callback(f"Resolution {resolution} not available. Getting highest resolution...")
                stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_highest_resolution()
            
        if progress_callback:
            progress_callback(f"Downloading: {stream.resolution}")
        
        if output_path:
            video_path = stream.download(output_path=output_path)
        else:
            video_path = stream.download()
            
        if progress_callback:
            progress_callback("Download completed with pytube!")
        return video_path
    except Exception as e:
        if progress_callback:
            progress_callback(f"pytube download failed: {e}")
        return None

def download_with_ytdlp(link, output_path=None, resolution=None, progress_callback=None):
    """Download video using yt-dlp (most powerful option)"""
    try:
        if not output_path:
            output_path = os.getcwd()
            
        # Configure yt-dlp options
        ydl_opts = {
            'format': f'bestvideo[height<={resolution[:-1]}]+bestaudio/best' if resolution else 'best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [lambda d: progress_callback(f"Progress: {d['_percent_str']}") if progress_callback and '_percent_str' in d else None]
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            video_path = ydl.prepare_filename(info)
            if progress_callback:
                progress_callback("Download completed with yt-dlp!")
            return video_path
    except Exception as e:
        if progress_callback:
            progress_callback(f"yt-dlp download failed: {e}")
        return None

def extract_audio(video_path, audio_format="mp3", progress_callback=None):
    """Extract audio from video file"""
    try:
        audio_path = os.path.splitext(video_path)[0] + f".{audio_format}"
        
        # Load the video file and extract audio
        with VideoFileClip(video_path) as video:
            if audio_format == "flac":
                video.audio.write_audiofile(audio_path, codec="flac", logger=None)
            else:
                video.audio.write_audiofile(audio_path, logger=None)
        
        if progress_callback:
            progress_callback(f"Audio extracted to {audio_path}")
        return audio_path
    except Exception as e:
        if progress_callback:
            progress_callback(f"Audio extraction failed: {e}")
        return None

def download_video(video_link, output_path=None, resolution=None, extract_audio_option=False, audio_format="mp3", progress_callback=None):
    """Main function to download video and extract audio if needed"""
    try:
        # Try downloading with different methods
        if progress_callback:
            progress_callback("Attempting download with pytubefix...")
        video_path = download_with_pytubefix(video_link, output_path, resolution, progress_callback)
        
        if not video_path:
            if progress_callback:
                progress_callback("Attempting download with pytube...")
            video_path = download_with_pytube(video_link, output_path, resolution, progress_callback)
            
        if not video_path:
            if progress_callback:
                progress_callback("Attempting download with yt-dlp (most powerful)...")
            video_path = download_with_ytdlp(video_link, output_path, resolution, progress_callback)
            
        if not video_path:
            if progress_callback:
                progress_callback("All download methods failed. Please check the URL or try again later.")
            return None
            
        # Extract audio if requested
        if extract_audio_option:
            audio_path = extract_audio(video_path, audio_format, progress_callback)
            return video_path, audio_path
        
        if progress_callback:
            progress_callback("Process completed successfully!")
        return video_path, None
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"An error occurred: {e}")
        return None, None