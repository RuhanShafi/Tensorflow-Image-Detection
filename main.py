import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow
from ui.theme import STYLESHEET
from model.loader import Predictor

###app = QApplication(sys.argv)
##msg = QMessageBox()
##msg.setWindowTitle("Hello, World!")
##msg.setText("This is a simple message.")
##msg.exec_()
### 

MODEL_PATH = "model/model.tflite"
#PDF_PATH = "docs/model_explainer.pdf"

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    try:
        predictor = Predictor(MODEL_PATH)
    except Exception as e:
        QMessageBox.critical(None, "Model Load Error", f"Could not load model:\n{e}")
        sys.exit(1)

    window = MainWindow(predictor=predictor)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()