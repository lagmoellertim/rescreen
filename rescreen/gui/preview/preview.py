from typing import List, Optional

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from rescreen.gui.main_controller import MainController
from rescreen.gui.preview.preview_item import PreviewItem


class Preview(QGraphicsView):
    def __init__(self, parent=None):
        super(Preview, self).__init__(parent)
        self.controller: Optional[MainController] = None
        self.current_scale = 1
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

        self.preview_items: List[PreviewItem] = []

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_controller(self, controller: MainController):
        self.controller = controller
        self.controller.on_current_display_config_changed.connect(self.update_display_previews)

    def update_display_previews(self):
        if not self.controller.get_current_state():
            return

        background_color = self.palette().color(QPalette.Normal, QPalette.Mid)

        scene = QGraphicsScene(backgroundBrush=background_color)
        self.setScene(scene)
        self.preview_items = []

        for display in self.controller.get_current_state().active_displays:
            item = PreviewItem(self.controller, self, display)
            item.setX(display.virtual_offset[0])
            item.setY(display.virtual_offset[1])

            scene.addItem(item)
            self.preview_items.append(item)

        self.redraw()

        for item in self.preview_items:
            item.on_current_display_changed()

    def mouseReleaseEvent(self, event):
        super(Preview, self).mouseReleaseEvent(event)
        self.redraw()

    def resizeEvent(self, event):
        super(Preview, self).resizeEvent(event)
        self.redraw()

    def redraw(self):
        if len(self.preview_items) == 0:
            return

        min_x = min([item.x() for item in self.preview_items])
        min_y = min([item.y() for item in self.preview_items])

        for item in self.preview_items:
            offset = (item.x() - min_x, item.y() - min_y)

            item.setX(offset[0])
            item.setY(offset[1])

            self.controller.set_display_offset(item.display, offset)

        max_x = max([item.x() + item.rect().width() for item in self.preview_items])
        max_y = max([item.y() + item.rect().height() for item in self.preview_items])

        self.setSceneRect(QRectF(0, 0, max_x, max_y))

        self.resetTransform()
        self.current_scale = min(self.width() / max_x, self.height() / max_y) / 1.5
        self.scale(self.current_scale, self.current_scale)
