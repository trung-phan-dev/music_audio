import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QCheckBox, QFileDialog, QTextEdit, 
                            QProgressBar, QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import pyqtSignal, QObject, Qt

# Import from our package
from youtube_downloader.core.downloader import download_video
from youtube_downloader.utils.helpers import (get_default_download_dir, 
                                             ensure_dir_exists,
                                             get_available_resolutions,
                                             get_audio_formats)

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)

class DownloadWorker(threading.Thread):
    """Worker thread for downloading videos"""
    def __init__(self, url, output_path, resolution, extract_audio, audio_format):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.resolution = resolution
        self.extract_audio = extract_audio
        self.audio_format = audio_format
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            result = download_video(
                self.url, 
                self.output_path, 
                self.resolution, 
                self.extract_audio, 
                self.audio_format,
                self.signals.progress.emit
            )
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(600, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # URL input section
        url_group = QGroupBox("YouTube URL")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube video URL")
        url_layout.addWidget(self.url_input)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)
        
        # Output directory section
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setText(get_default_download_dir())
        self.output_path.setReadOnly(True)
        output_layout.addWidget(self.output_path)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        output_layout.addWidget(browse_btn)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Video options section
        video_group = QGroupBox("Video Options")
        video_layout = QHBoxLayout()
        
        # Resolution selection
        resolution_layout = QVBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("Best Available")
        for res in get_available_resolutions():
            self.resolution_combo.addItem(res)
        resolution_layout.addWidget(self.resolution_combo)
        video_layout.addLayout(resolution_layout)
        
        # Audio extraction options
        audio_layout = QVBoxLayout()
        self.extract_audio_cb = QCheckBox("Extract Audio")
        audio_layout.addWidget(self.extract_audio_cb)
        
        audio_format_layout = QHBoxLayout()
        self.mp3_radio = QRadioButton("MP3")
        self.flac_radio = QRadioButton("FLAC")
        self.mp3_radio.setChecked(True)
        audio_format_layout.addWidget(self.mp3_radio)
        audio_format_layout.addWidget(self.flac_radio)
        
        audio_format_group = QButtonGroup(self)
        audio_format_group.addButton(self.mp3_radio)
        audio_format_group.addButton(self.flac_radio)
        
        audio_layout.addLayout(audio_format_layout)
        video_layout.addLayout(audio_layout)
        
        video_group.setLayout(video_layout)
        main_layout.addWidget(video_group)
        
        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setMinimumHeight(40)
        main_layout.addWidget(self.download_btn)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        progress_layout.addWidget(self.log_output)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
    def browse_directory(self):
        """Open file dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.output_path.text()
        )
        if directory:
            self.output_path.setText(directory)
            
    def start_download(self):
        """Start the download process in a separate thread"""
        url = self.url_input.text().strip()
        if not url:
            self.log_message("Please enter a YouTube URL")
            return
            
        output_path = self.output_path.text()
        ensure_dir_exists(output_path)
        
        resolution = None
        if self.resolution_combo.currentIndex() > 0:
            resolution = self.resolution_combo.currentText()
            
        extract_audio = self.extract_audio_cb.isChecked()
        audio_format = "mp3" if self.mp3_radio.isChecked() else "flac"
        
        # Disable UI elements during download
        self.download_btn.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Clear log
        self.log_output.clear()
        self.log_message("Starting download...")
        
        # Create and start worker thread
        self.worker = DownloadWorker(url, output_path, resolution, extract_audio, audio_format)
        self.worker.signals.progress.connect(self.log_message)
        self.worker.signals.finished.connect(self.download_finished)
        self.worker.signals.error.connect(self.download_error)
        self.worker.start()
        
    def log_message(self, message):
        """Add message to log output"""
        self.log_output.append(message)
        # Auto-scroll to bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
        
    def download_finished(self, result):
        """Handle download completion"""
        video_path, audio_path = result
        
        if video_path:
            self.log_message(f"Download completed successfully!")
            if audio_path:
                self.log_message(f"Audio extracted to: {os.path.basename(audio_path)}")
        else:
            self.log_message("Download failed.")
            
        # Re-enable UI elements
        self.download_btn.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
    def download_error(self, error_message):
        """Handle download errors"""
        self.log_message(f"Error: {error_message}")
        self.download_btn.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)