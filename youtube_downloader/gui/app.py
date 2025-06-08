import sys
from PyQt5.QtWidgets import QApplication
from youtube_downloader.gui.main_window import MainWindow

def run_app():
    """Run the GUI application"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())