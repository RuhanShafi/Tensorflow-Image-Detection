from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from ui.pdf_renderer import PDFRenderer


class PDFOverlay(QWidget):
    """Displays a rendered PDF page with prev/next navigation and a close
    button. Purely a viewer — MainWindow decides when it's shown/hidden."""

    def __init__(self, pdf_path, on_close, parent=None):
        super().__init__(parent)
        self.on_close = on_close
        self.current_page = 0

        try:
            self.renderer = PDFRenderer(pdf_path)
            self.load_error = None
        except RuntimeError as e:
            self.renderer = None
            self.load_error = str(e)

        self._build_ui()

        if self.renderer:
            self._show_page(0)
        else:
            self.page_label.setText(self.load_error)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # --- Top bar: close button ---
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.on_close)
        top_bar.addWidget(close_btn)
        layout.addLayout(top_bar)

        # --- Page display ---
        self.page_label = QLabel()
        self.page_label.setObjectName("pdfPage")
        self.page_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.page_label, stretch=1)

        # --- Bottom bar: prev/next + page indicator ---
        nav_bar = QHBoxLayout()
        self.prev_btn = QPushButton("< Prev")
        self.prev_btn.clicked.connect(self._prev_page)
        nav_bar.addWidget(self.prev_btn)

        self.page_indicator = QLabel()
        self.page_indicator.setAlignment(Qt.AlignCenter)
        nav_bar.addWidget(self.page_indicator, stretch=1)

        self.next_btn = QPushButton("Next >")
        self.next_btn.clicked.connect(self._next_page)
        nav_bar.addWidget(self.next_btn)

        layout.addLayout(nav_bar)

    def _show_page(self, index):
        pixmap = self.renderer.render_page(index)
        scaled = pixmap.scaled(
            self.page_label.width() or pixmap.width(),
            self.page_label.height() or pixmap.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.page_label.setPixmap(scaled)
        self.current_page = index
        self.page_indicator.setText(f"Page {index + 1} of {self.renderer.page_count}")

        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < self.renderer.page_count - 1)

    def _prev_page(self):
        if self.renderer and self.current_page > 0:
            self._show_page(self.current_page - 1)

    def _next_page(self):
        if self.renderer and self.current_page < self.renderer.page_count - 1:
            self._show_page(self.current_page + 1)

    def resizeEvent(self, event):
        if self.renderer:
            self._show_page(self.current_page)  # re-render at new size
        super().resizeEvent(event)