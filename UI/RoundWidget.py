from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtCore import Qt, QRectF


class RoundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fill_color = None
        self.setFixedSize(52, 52)
        self.is_fill = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.black)

        if self.fill_color:
            painter.setBrush(QBrush(self.fill_color))

        rect = QRectF(2, 2, 48, 48)
        painter.drawEllipse(rect)

    def setFilled(self, fill, color=Qt.red):
        if fill is not None:
            self.is_fill = fill
        else:
            self.is_fill = not self.is_fill
        if self.is_fill:
            self.fill_color = color
        else:
            self.fill_color = None
        self.update()

