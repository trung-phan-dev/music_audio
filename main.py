from pytubefix import YouTube
from pytubefix import YouTube as PyTube
import yt_dlp
from moviepy.editor import VideoFileClip
import os
import re
import sys

def sanitize_filename(title):
    """Remove invalid characters from filename"""
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_with_pytubefix(link, output_path=None, resolution=None):
    """Download video using pytubefix library"""
    try:
        yt = YouTube(link)
        print(f"Title: {yt.title}")
        print(f"Length: {yt.length} seconds")
        
        if resolution:
            stream = yt.streams.filter(res=resolution).first()
            if not stream:
                print(f"Resolution {resolution} not available. Getting highest resolution...")
                stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_highest_resolution()
            
        print(f"Downloading: {stream.resolution}")
        
        if output_path:
            video_path = stream.download(output_path=output_path)
        else:
            video_path = stream.download()
            
        print("Download completed with pytubefix!")
        return video_path
    except Exception as e:
        print(f"pytubefix download failed: {e}")
        return None

def download_with_pytube(link, output_path=None, resolution=None):
    """Download video using standard pytube library"""
    try:
        yt = PyTube(link)
        print(f"Title: {yt.title}")
        print(f"Length: {yt.length} seconds")
        
        if resolution:
            stream = yt.streams.filter(res=resolution).first()
            if not stream:
                print(f"Resolution {resolution} not available. Getting highest resolution...")
                stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.get_highest_resolution()
            
        print(f"Downloading: {stream.resolution}")
        
        if output_path:
            video_path = stream.download(output_path=output_path)
        else:
            video_path = stream.download()
            
        print("Download completed with pytube!")
        return video_path
    except Exception as e:
        print(f"pytube download failed: {e}")
        return None

def download_with_ytdlp(link, output_path=None, resolution=None):
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
            'no_warnings': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            video_path = ydl.prepare_filename(info)
            print("Download completed with yt-dlp!")
            return video_path
    except Exception as e:
        print(f"yt-dlp download failed: {e}")
        return None

def extract_audio(video_path, audio_format="mp3"):
    """Extract audio from video file"""
    try:
        audio_path = os.path.splitext(video_path)[0] + f".{audio_format}"
        
        # Load the video file and extract audio
        with VideoFileClip(video_path) as video:
            if audio_format == "flac":
                video.audio.write_audiofile(audio_path, codec="flac")
            else:
                video.audio.write_audiofile(audio_path)
        print(f"Audio extracted to {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Audio extraction failed: {e}")
        return None

def download_video():
    """Main function to download video and extract audio if needed"""
    try:
        # Get video link
        video_link = input("Enter the YouTube video URL: ")
        
        # Ask for output directory
        use_custom_dir = input("Use custom output directory? (y/n): ").lower() == 'y'
        output_path = None
        if use_custom_dir:
            output_path = input("Enter output directory path: ")
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        
        # Ask for resolution
        use_custom_res = input("Specify video resolution? (y/n): ").lower() == 'y'
        resolution = None
        if use_custom_res:
            print("Available resolutions: 144p, 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p")
            resolution = input("Enter desired resolution (e.g. 720p): ")
        
        # Try downloading with different methods
        print("\nAttempting download with pytubefix...")
        video_path = download_with_pytubefix(video_link, output_path, resolution)
        
        if not video_path:
            print("\nAttempting download with pytube...")
            video_path = download_with_pytube(video_link, output_path, resolution)
            
        if not video_path:
            print("\nAttempting download with yt-dlp (most powerful)...")
            video_path = download_with_ytdlp(video_link, output_path, resolution)
            
        if not video_path:
            print("All download methods failed. Please check the URL or try again later.")
            return
            
        # Ask if user wants to extract audio
        extract_audio_option = input("Extract audio? (y/n): ").lower() == 'y'
        if extract_audio_option:
            print("Select audio format:")
            print("1: mp3 format")
            print("2: flac format")
            user_option = input("Enter option (1/2): ")
            
            audio_format = "mp3"
            if user_option == "2":
                audio_format = "flac"
                
            extract_audio(video_path, audio_format)
            
        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_video()