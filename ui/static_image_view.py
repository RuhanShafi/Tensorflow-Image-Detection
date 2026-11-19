import os

import cv2
import numpy as np
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

from ui.webcam_view import (
    FACE_CASCADE,
    CONFIDENCE_THRESHOLD,
    padded_crop,
    draw_face_box,
)


IMAGE_FILE_FILTER = (
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;All files (*)"
)

# Smallest face to look for, as a fraction of the image's shorter side.
# Relative (not a fixed pixel size like the webcam's 80px) because still
# images range from small thumbnails to 4000px+ phone photos, and group
# photos often contain faces far smaller than a webcam close-up.
MIN_FACE_FRACTION = 0.04
MIN_FACE_PX = 24
DETECTION_MAX_SIDE = 1024  # longest side of the copy used for face detection

# Eye-based verification of face candidates (see _has_eye).
# The eyeglasses variant still finds eyes behind glasses.
EYE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml"
)
EYE_SEARCH_FRACTION = 0.6  # eyes sit in the upper ~60% of a Haar face box
EYE_CHECK_FACE_PX = 200  # face crop width normalised to this before eye search

# Reference size the webcam overlay styling was tuned for; larger images
# get proportionally thicker boxes / bigger text so labels stay readable
# after the image is scaled down to fit the window.
OVERLAY_REFERENCE_PX = 800


def load_image_rgb(path):
    """Read an image file into an RGB uint8 array. Uses imdecode on raw
    bytes rather than cv2.imread so non-ASCII paths work on Windows."""
    data = np.fromfile(path, dtype=np.uint8)
    image_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise ValueError("File is not a supported image format.")
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def detect_faces(image_rgb):
    """Return a list of (x, y, w, h) boxes, in full-resolution coordinates,
    for every face in a still image.

    Detection runs on a copy downscaled to DETECTION_MAX_SIDE: the Haar
    cascade is tuned for webcam-sized frames, and on 4000px phone photos it
    fires on fabric/hair texture. Boxes are scaled back up so classification
    still uses full-resolution crops."""
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    ratio = min(1.0, DETECTION_MAX_SIDE / max(gray.shape[:2]))
    if ratio < 1.0:
        gray = cv2.resize(gray, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)

    min_side = max(MIN_FACE_PX, int(min(gray.shape[:2]) * MIN_FACE_FRACTION))
    faces = FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_side, min_side)
    )
    boxes = [tuple(int(round(v / ratio)) for v in f) for f in faces]

    # A still image gets a single detection pass with no tracking to smooth
    # out spurious hits, so confirm each candidate actually contains an eye.
    full_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    return [box for box in boxes if _has_eye(full_gray, box)]


def _has_eye(gray, bbox):
    """True if at least one eye is found in the upper part of a face box.
    Filters out Haar false positives on clothing, hair and background."""
    x, y, w, h = bbox
    roi = gray[y : y + int(h * EYE_SEARCH_FRACTION), x : x + w]
    if roi.size == 0:
        return False
    # Normalise face width so the eye cascade sees a consistent scale
    # regardless of how large the face is in the source image.
    s = EYE_CHECK_FACE_PX / w
    roi = cv2.resize(
        roi,
        None,
        fx=s,
        fy=s,
        interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR,
    )
    eyes = EYE_CASCADE.detectMultiScale(
        roi, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20)
    )
    return len(eyes) > 0


class StaticImageView(QWidget):
    """Shows a user-chosen image with a bounding box + prediction for every
    detected face. Same overlay style as WebcamView, but each face is
    classified exactly once (no tracking/smoothing needed for a still).

    on_predict: callable(rgb_face_crop) -> (label: str, confidence: float)
    """

    def __init__(self, on_predict, parent=None):
        super().__init__(parent)
        self.on_predict = on_predict
        self.image_path = None
        self.annotated_rgb = None  # kept so the view can rescale on resize

        self._build_ui()

    # ---------- UI ----------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        controls = QHBoxLayout()
        self.file_label = QLabel("No image loaded")
        controls.addWidget(self.file_label, stretch=1)

        self.change_btn = QPushButton("Change Image")
        self.change_btn.clicked.connect(self.prompt_for_image)
        controls.addWidget(self.change_btn)
        layout.addLayout(controls)

        self.preview_label = QLabel("No image loaded")
        self.preview_label.setObjectName("webcamPreview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(360)
        # Ignore the pixmap's own size so the label follows the window
        # (and can shrink) instead of growing to fit the scaled image.
        self.preview_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout.addWidget(self.preview_label, stretch=1)

    # ---------- Loading ----------

    def prompt_for_image(self):
        """Open the system file browser. Returns True if a new image was
        loaded, False if the user cancelled or the file couldn't be read."""
        start_dir = os.path.dirname(self.image_path) if self.image_path else ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select an image", start_dir, IMAGE_FILE_FILTER
        )
        if not path:
            return False
        return self.load_image(path)

    def load_image(self, path):
        try:
            image_rgb = load_image_rgb(path)
        except Exception as e:
            self.file_label.setText(f"Could not open {os.path.basename(path)}: {e}")
            return False

        self.image_path = path
        faces = detect_faces(image_rgb)

        # Classify on the clean image, then draw — so one face's box/label
        # can never bleed into a neighbouring face's crop.
        predictions = [self._classify(image_rgb, bbox) for bbox in faces]

        annotated = image_rgb.copy()
        scale = max(1.0, max(annotated.shape[:2]) / OVERLAY_REFERENCE_PX)
        for bbox, prediction in zip(faces, predictions):
            draw_face_box(annotated, bbox, prediction, scale=scale)

        self.annotated_rgb = annotated
        count = len(faces)
        summary = f"{count} face{'s' if count != 1 else ''} detected"
        self.file_label.setText(f"{os.path.basename(path)} — {summary}")
        self._refresh_pixmap()
        return True

    def _classify(self, image_rgb, bbox):
        crop = padded_crop(image_rgb, bbox)
        if crop.size == 0:
            return None
        result = self.on_predict(crop)
        if result is None:
            return None
        label, confidence = result
        return label, confidence, confidence >= CONFIDENCE_THRESHOLD

    # ---------- Display ----------

    def _refresh_pixmap(self):
        if self.annotated_rgb is None:
            return
        rgb = np.ascontiguousarray(self.annotated_rgb)
        h, w, ch = rgb.shape
        qimage = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage).scaled(
            self.preview_label.width(),
            self.preview_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_pixmap()
