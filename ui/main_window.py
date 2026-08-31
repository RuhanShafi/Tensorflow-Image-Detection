from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame,
    QDockWidget, QPushButton
)
from PySide6.QtCore import Qt

#from ui.theme import STYLESHEET, MOCHA

CLASS_NAMES = ["Man", "Boys", "Woman", "Girls"]


class MainWindow(QMainWindow):
    def __init__(self, predictor, pdf_path):
        super().__init__()
        self.predictor = predictor
        self.setWindowTitle("CNN Live Demo")
        self.resize(900, 650)

    def _build_central(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Face Classifier")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.view_panel = QFrame()
        self.view_panel.setObjectName("viewPanel")
        self.view_panel.setFrameShape(QFrame.StyledPanel)
        self.view_panel.setMinimumHeight(420)

        panel_layout = QVBoxLayout(self.view_panel)
        placeholder = QLabel("[ Webcam / Image View ]")
        placeholder.setObjectName("placeholderLabel")
        placeholder.setAlignment(Qt.AlignCenter)
        panel_layout.addWidget(placeholder)

        layout.addWidget(self.view_panel)
        self.setCentralWidget(central)
