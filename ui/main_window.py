from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QTabWidget, QPushButton, QToolBar
)
from PySide6.QtGui import QAction

CLASS_NAMES = ['Man', 'Boys', 'Woman', 'Girls']

class MainWindow(QMainWindow):
    def __init__(self, predictor, pdf_path):
        super().__init__()
        self.predictor = predictor
        self.setWindowTitle("Face Classifier")
        self.resize(900, 650)
