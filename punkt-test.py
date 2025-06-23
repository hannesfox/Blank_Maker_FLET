from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
import sys

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(500, 300, 20, 20)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 10, 10)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        self.close()

app = QApplication(sys.argv)
overlay = Overlay()
overlay.setFocus()

# Damit App sauber endet, wenn Fenster geschlossen wird
overlay.destroyed.connect(app.quit)

sys.exit(app.exec_())
