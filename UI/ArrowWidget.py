from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPolygon, QBrush
from PyQt5.QtCore import Qt, QPoint


class ArrowWidget(QWidget):
    def __init__(self, parent, arrow_type):
        super().__init__(parent)
        self.arrow_type = arrow_type
        self.fill_color = None
        self.setFixedSize(52, 52)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.black)

        if self.fill_color:
            painter.setBrush(QBrush(self.fill_color))

        if self.arrow_type == 0:  # Up arrow
            points = [QPoint(25, 0), QPoint(50, 50), QPoint(0, 50)]
        elif self.arrow_type == 1:  # Down arrow
            points = [QPoint(25, 50), QPoint(0, 0), QPoint(50, 0)]
        elif self.arrow_type == 2:  # Left arrow
            points = [QPoint(0, 25), QPoint(50, 0), QPoint(50, 50)]
        elif self.arrow_type == 3:  # Right arrow
            points = [QPoint(50, 25), QPoint(0, 50), QPoint(0, 0)]
        else:
            raise ValueError("Invalid arrow type!")

        arrow = QPolygon(points)
        painter.drawPolygon(arrow)

    def setFilled(self, fill=True, color=Qt.red):
        if fill:
            self.fill_color = color
        else:
            self.fill_color = None
        self.update()
