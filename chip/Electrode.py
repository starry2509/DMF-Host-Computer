from PyQt5.QtCore import QPoint, QRectF, Qt
from PyQt5.QtGui import QColor, QPolygon, QStaticText, QPen, QPainterPath
from PyQt5.QtWidgets import QGraphicsItem


class Electrode(QGraphicsItem):
    name = "Electrode"

    def __init__(self, event=None, pos_list=None, ID=None, DriveID=None):
        super().__init__()
        if pos_list is None:
            pos_list = [[], []]
        self.isDrive = False
        self.isPinned = False
        self.showDriveID = True
        self.isTransparent = False
        self.ID = ID
        self.DriveID = self.ID if DriveID is None else DriveID
        self.x_cord = list(pos_list[0])
        self.x_cord.append(self.x_cord[0])
        self.y_cord = list(pos_list[1])
        self.y_cord.append(self.y_cord[0])
        self.W = max(self.x_cord) - min(self.x_cord)
        self.H = max(self.y_cord) - min(self.y_cord)
        self.x0 = int(min(self.x_cord))
        self.y0 = int(min(self.y_cord))
        self.xcenter = sum(self.x_cord) / len(self.x_cord)
        self.ycenter = sum(self.y_cord) / len(self.y_cord)
        self.points = [QPoint(int(x), int(y)) for x, y in zip(self.x_cord, self.y_cord)]
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

    def setDriveStatus(self, status=True):
        if self.isPinned and not status:
            return
        self.isDrive = status
        self.update()

    def changeDriveStatus(self):
        if self.isPinned:
            return
        self.isDrive = not self.isDrive
        self.update()

    def changeSelectStatus(self):
        if self.isPinned:
            return
        self.setSelected(not self.isSelected())
        self.update()

    def setPinned(self, pinned=True):
        self.isPinned = pinned
        if pinned:
            self.isDrive = True
            self.setSelected(True)
        self.update()

    def togglePinned(self):
        self.setPinned(not self.isPinned)

    def boundingRect(self):
        return QRectF(self.x0, self.y0, self.W, self.H)

    def paint(self, painter, option, widget):
        if self.isPinned:
            color = QColor(156, 39, 176, 255)
        elif self.isSelected() and self.isDrive:
            color = QColor(238, 130, 47, 255)
        elif self.isSelected():
            color = QColor(72, 126, 203, 255)
        elif self.isDrive:
            color = QColor(0, 176, 80, 255)
        else:
            color = QColor(19, 195, 169, 255)
        if self.isTransparent:
            color = QColor(color.red(), color.green(), color.blue(), 150)
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawPolygon(QPolygon(self.points), len(self.points))
        if not self.showDriveID:
            return
        painter.setPen(QColor(255, 255, 255))
        text = QStaticText()
        text.setTextWidth(self.W / 2)
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setText(f"<b>{self.DriveID:.0f}</b>")
        painter.drawStaticText(
            int(self.xcenter - 0.5 * text.size().width()),
            int(self.ycenter - 0.5 * text.size().height()),
            text,
        )

    def shape(self):
        path = QPainterPath()
        for i, (x, y) in enumerate(zip(self.x_cord, self.y_cord)):
            if i == 0:
                path.moveTo(int(x), int(y))
            else:
                path.lineTo(int(x), int(y))
        path.closeSubpath()
        return path
