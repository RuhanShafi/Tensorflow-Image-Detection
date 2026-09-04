import  pymupdf
from PySide6.QtGui import QImage, QPixmap

RENDER_DPI = 150


class PDFRenderer:
    """Loads a PDF once and renders individual pages to QPixmap on demand.
    No widget/layout logic here — pure document access."""

    def __init__(self, pdf_path):
        try:
            self.doc = pymupdf.open(pdf_path)
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF '{pdf_path}': {e}") from e

        if self.doc.page_count == 0:
            raise RuntimeError(f"PDF '{pdf_path}' has no pages")

    @property
    def page_count(self):
        return self.doc.page_count

    def render_page(self, index: int) -> QPixmap:
        if not (0 <= index < self.page_count):
            raise IndexError(f"Page {index} out of range (0-{self.page_count - 1})")

        page = self.doc.load_page(index)
        zoom = RENDER_DPI / 72  # PDF points are 72 dpi by default
        matrix = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)

        image_format = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, image_format)
        return QPixmap.fromImage(qimage)

    def close(self):
        self.doc.close()