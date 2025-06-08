# YouTube Downloader with GUI

A GUI application for downloading YouTube videos and extracting audio.

## Features

- Download YouTube videos with selectable resolution
- Extract audio in MP3 or FLAC format
- User-friendly graphical interface
- Multiple download methods for better reliability

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the GUI application:

```bash
python main_gui.py
```

The command-line version is still available:

```bash
python main.py
```

## Project Structure

```
youtube_downloader/
├── core/               # Core functionality
│   └── downloader.py   # Download and extraction logic
├── gui/                # GUI components
│   ├── app.py          # Application launcher
│   └── main_window.py  # Main window interface
└── utils/              # Utility functions
    └── helpers.py      # Helper functions
```

## Requirements

- Python 3.6+
- PyQt5
- pytubefix
- yt-dlp
- moviepy