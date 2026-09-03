import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

MAX_PROBE_INDEX = 5          # how many device indices to check on startup
PREVIEW_INTERVAL_MS = 30     # ~33 fps preview
PREDICT_EVERY_N_FRAMES = 15  # throttle inference vs. preview


class WebcamView(QWidget):
    """Live webcam preview with device selection. Calls on_predict(rgb_frame)
    periodically while running; caller is responsible for showing the result."""

    def __init__(self, on_predict, parent=None):
        super().__init__(parent)
        self.on_predict = on_predict
        self.capture = None
        self.frame_count = 0

        self._build_ui()
        self._populate_devices()
        self._start_camera(self.device_combo.currentData())

    # ---------- UI ----------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Camera:"))

        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)
        controls.addWidget(self.device_combo, stretch=1)
        layout.addLayout(controls)

        self.preview_label = QLabel("No camera")
        self.preview_label.setObjectName("webcamPreview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(360)
        layout.addWidget(self.preview_label, stretch=1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_frame)

    # ---------- Device enumeration ----------

    def _populate_devices(self):
        """Probe indices 0..MAX_PROBE_INDEX-1, keep the ones that actually open.
        Index 0 (if available) is treated as the system default and selected first."""
        self.device_combo.blockSignals(True)
        self.device_combo.clear()

        found_any = False
        for index in range(MAX_PROBE_INDEX):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                label = "Default Camera" if index == 0 else f"Camera {index}"
                self.device_combo.addItem(label, userData=index)
                found_any = True
            cap.release()

        self.device_combo.blockSignals(False)

        if not found_any:
            self.device_combo.addItem("No camera found", userData=None)

    # ---------- Camera lifecycle ----------

    def _start_camera(self, index):
        self._stop_camera()

        if index is None:
            self.preview_label.setText("No camera available")
            return

        self.capture = cv2.VideoCapture(index)
        if not self.capture.isOpened():
            self.preview_label.setText(f"Could not open camera {index}")
            self.capture = None
            return

        self.frame_count = 0
        self.timer.start(PREVIEW_INTERVAL_MS)

    def _stop_camera(self):
        self.timer.stop()
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def _on_device_changed(self, _ui_index):
        selected = self.device_combo.currentData()
        self._start_camera(selected)

    # ---------- Frame loop ----------

    def _on_frame(self):
        if self.capture is None:
            return

        ok, frame_bgr = self.capture.read()
        if not ok:
            return

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        self._show_frame(frame_rgb)

        self.frame_count += 1
        if self.frame_count % PREDICT_EVERY_N_FRAMES == 0:
            self.on_predict(frame_rgb)

    def _show_frame(self, frame_rgb):
        h, w, ch = frame_rgb.shape
        qimage = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage).scaled(
            self.preview_label.width(), self.preview_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)

    # ---------- Cleanup ----------

    def closeEvent(self, event):
        self._stop_camera()
        super().closeEvent(event)

    def hideEvent(self, event):
        # Pause capture when the tab/view isn't visible (e.g. user switched to
        # Static Image), so we're not holding the device or burning CPU idly.
        self.timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):
        if self.capture is not None:
            self.timer.start(PREVIEW_INTERVAL_MS)
        super().showEvent(event)