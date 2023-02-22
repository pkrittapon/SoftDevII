import threading
import yfinance as yf
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QProgressBar, QVBoxLayout, QPushButton, QLabel

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Stock Data Downloader")
        self.resize(300, 200)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.download_label = QLabel("Click the button to download stock data.")
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.download_label)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def download(self):
        self.download_label.setText("Downloading stock data...")
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # Create a new thread to perform the download
        download_thread = threading.Thread(target=self.download_stock_data)
        download_thread.start()

    def download_stock_data(self):
        data = yf.download("AAPL", period="1mo")
        self.progress_bar.setValue(100)
        self.download_label.setText("Stock data downloaded successfully.")
        self.download_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
