from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QDockWidget, QPushButton, QStackedWidget
)
from PySide6.QtCore import Qt

from ui.theme import STYLESHEET, MOCHA
from ui.webcam_view import WebcamView


class MainWindow(QMainWindow):
    def __init__(self, predictor=None):
        super().__init__()
        self.predictor = predictor
        self.setWindowTitle("Face Classifier")
        self.resize(1000, 700)
        self.setStyleSheet(STYLESHEET)

        self._build_central()
        self._build_toolbar_dock()

    def _build_central(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # --- Title ---
        title = QLabel("Face Classifier")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Content area: webcam view lives here for now, will become a
        # QStackedWidget holding WebcamView / ImageView / PDFOverlay once
        # those other pieces exist. ---
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("viewPanel")

        self.webcam_view = WebcamView(on_predict=self._run_prediction)
        self.content_stack.addWidget(self.webcam_view)  # index 0

        layout.addWidget(self.content_stack, stretch=1)
        self.setCentralWidget(central)

    def _build_toolbar_dock(self):
        dock = QDockWidget("Controls", self)
        dock.setObjectName("controlsDock")
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        dock_content = QWidget()
        dock_layout = QVBoxLayout(dock_content)
        dock_layout.setContentsMargins(12, 12, 12, 12)
        dock_layout.setSpacing(10)
        dock_layout.setAlignment(Qt.AlignTop)

        self.webcam_btn = QPushButton("Webcam")
        self.static_btn = QPushButton("Static Image")
        self.pdf_toggle_btn = QPushButton("Toggle Model Info")

        for btn in (self.webcam_btn, self.static_btn, self.pdf_toggle_btn):
            dock_layout.addWidget(btn)

        dock.setWidget(dock_content)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _run_prediction(self, image):
        """Callback passed to WebcamView — called periodically with an RGB frame."""
        if self.predictor is None:
            return  # no model wired up yet
        label, confidence = self.predictor.predict(image)
        print(f"{label} ({confidence:.2%})")  # placeholder until result_panel exists


if __name__ == "__main__":
    # Quick standalone preview: `python -m ui.main_window`
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())