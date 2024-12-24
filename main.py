from pytubefix import YouTube
from moviepy.editor import VideoFileClip
import os

"""To use this code, install python package pytubefix"""

def download_video(link):
    try:
        # Create a YouTube object
        yt = YouTube(link)

        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()

        # Download the video
        print("Downloading video...")
        video_path = stream.download()
        print("Download completed!")

        # Extract audio from the downloaded video
        print("Selecting format audio")
        user_options = input("1: mp3 format archive | 2: flac format archive ->")
        if user_options == "1":
            audio_format = "mp3"
        elif user_options == "2":
            audio_format = "flac"
        audio_path = os.path.splitext(video_path)[0] + f".{audio_format}"
        
        # Load the video file and extract audio
        with VideoFileClip(video_path) as video:
            if audio_format == "flac":
                video.audio.write_audiofile(audio_path, codec="flac")
            else:
                video.audio.write_audiofile(audio_path)
        print(f"Audio extracted to {audio_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_link = input("Enter the YouTube video URL: ")
    download_video(video_link)
