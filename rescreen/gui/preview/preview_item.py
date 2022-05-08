import math
from typing import Optional

import PySide6.QtGui
import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from rescreen.gui.main_controller import MainController
from rescreen.lib.interfaces import Orientation
from rescreen.lib.state import DisplayState

if False:
    from rescreen.gui.preview.preview import Preview


class PreviewItem(QGraphicsRectItem):
    SNAPPING_DISTANCE = 15
    CHECKER_BOARD_BASE_SIZE = 30
    FONT_SIZE = 20
    TEXT_CONTAINER_PADDING = 10
    TEXT_CONTAINER_MARGIN = 15
    TEXT_CONTAINER_ROUNDING = 5
    PRIMARY_BAR_HEIGHT = 10

    def __init__(
        self,
        controller: MainController,
        preview: "Preview",
        display: DisplayState,
    ):
        super(PreviewItem, self).__init__()
        self.display = display

        self.__controller = controller
        self.__preview = preview

        self.__display_width = int(self.display.resolution[0] * self.display.resolution_scale)
        self.__display_height = int(self.display.resolution[1] * self.display.resolution_scale)

        if self.display.orientation in [Orientation.LEFT, Orientation.RIGHT]:
            self.__display_width, self.__display_height = (
                self.__display_height,
                self.__display_width,
            )

        self.setRect(QRectF(0, 0, self.__display_width, self.__display_height))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.__controller.on_current_display_changed.connect(self.on_current_display_changed)

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: Optional[PySide6.QtWidgets.QWidget] = ...,
    ) -> None:
        super().paint(painter, option, widget)

        painter.setRenderHint(QPainter.Antialiasing)

        scaling = self.__preview.current_scale

        # Define Colors
        font_color = self.__preview.palette().color(QPalette.Normal, QPalette.ButtonText)
        bg_color = self.__preview.palette().color(QPalette.Normal, QPalette.Button)
        dark = self.__preview.palette().color(QPalette.Normal, QPalette.Dark)

        # Apply Font Settings
        font = painter.font()
        scaled_font_size = self.FONT_SIZE / scaling
        font.setPointSize(scaled_font_size)
        painter.setFont(font)

        # Generate Text to display
        sorted_display_numbers = sorted(
            [
                display.metadata.display_number
                for display in self.__controller.get_current_state().get_mirrored_displays(
                    self.display
                )
            ]
        )

        text = " + ".join([str(x) for x in [self.display.display_number, *sorted_display_numbers]])

        # Calculate Scaled Variables
        scaled_padding = self.TEXT_CONTAINER_PADDING / scaling
        scaled_margin = self.TEXT_CONTAINER_MARGIN / scaling
        scaled_rounding = self.TEXT_CONTAINER_ROUNDING / scaling
        scaled_primary_bar = self.PRIMARY_BAR_HEIGHT / scaling

        # Draw Active Display Bar
        if self.display.primary:
            painter.fillRect(QRect(0, 0, self.__display_width, scaled_primary_bar), dark)

        # Draw Display Number Container
        path = QPainterPath()
        text_width = painter.boundingRect(0, 0, 0, 0, 0, text).width()
        path.addRoundedRect(
            QRect(
                scaled_margin,
                scaled_margin,
                text_width + scaled_padding * 2,
                scaled_font_size + scaled_padding * 2,
            ),
            scaled_rounding,
            scaled_rounding,
        )
        painter.fillPath(path, bg_color)

        # Draw Display Number
        painter.setPen(font_color)
        painter.drawText(
            scaled_margin + scaled_padding,
            scaled_font_size + scaled_margin + scaled_padding,
            text,
        )

    def get_pattern(self, active):
        square_size = (
            (self.CHECKER_BOARD_BASE_SIZE / self.__preview.current_scale)
            / self.display.resolution_scale
            * self.__controller.get_current_state().ui_scale
        )

        color_1 = self.__preview.palette().color(QPalette.Inactive, QPalette.Base)
        if active:
            color_1 = self.__preview.palette().color(QPalette.Inactive, QPalette.Highlight)

        color_2 = color_1.darker(110)

        pattern = QPixmap(square_size * 2, square_size * 2)
        painter = QPainter()
        pattern.fill(color_1)

        painter.begin(pattern)

        painter.fillRect(QRect(0, 0, square_size, square_size), color_2)
        painter.fillRect(
            QRect(square_size, square_size, square_size * 2, square_size * 2),
            color_2,
        )

        return pattern

    def on_current_display_changed(self):
        current_display = self.__controller.get_current_display()

        if current_display == self.display:
            for display in self.__preview.preview_items:
                if display != self:
                    display.stackBefore(self)

            self.setBrush(self.get_pattern(active=True))
        else:
            self.setBrush(self.get_pattern(active=False))

    def mousePressEvent(self, event):
        self.__controller.set_current_display(self.display)
        super(PreviewItem, self).mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            point: QPointF = value
            current = QRectF(
                point,
                point + QPointF(self.rect().width(), self.rect().height()),
            )

            dist = self.SNAPPING_DISTANCE / self.__preview.current_scale

            x_dist = float("+inf")
            y_dist = float("+inf")
            x_rect: Optional[QRectF] = None
            y_rect: Optional[QRectF] = None
            x_mode: Optional[int] = None
            y_mode: Optional[int] = None

            def order(display_preview: PreviewItem):
                current_center_x = point.x() + self.rect().width() / 2
                current_center_y = point.y() + self.rect().height() / 2
                other_center_x = display_preview.x() + display_preview.rect().width() / 2
                other_center_y = display_preview.y() + display_preview.rect().height() / 2

                return math.sqrt(
                    (other_center_x - current_center_x) ** 2
                    + (other_center_y - current_center_y) ** 2
                )

            for display in sorted(self.__preview.preview_items, key=order, reverse=True):
                other = QRectF(
                    QPointF(display.x(), display.y()),
                    QPointF(
                        display.x() + display.rect().width(),
                        display.y() + display.rect().height(),
                    ),
                )

                if display != self:
                    if (
                        abs(current.left() - other.left()) <= dist
                        and abs(current.top() - other.top()) <= dist
                        and current.width() == other.width()
                        and current.height() == other.height()
                    ):
                        return other.topLeft()

                    if current.bottom() >= other.top() and other.bottom() >= current.top():
                        if (val := abs(current.right() - other.left())) <= x_dist:
                            x_dist = val
                            x_mode = 0
                            x_rect = other

                        if (val := abs(other.right() - current.left())) <= x_dist:
                            x_dist = val
                            x_mode = 1
                            x_rect = other

                    if current.right() >= other.left() and other.right() >= current.left():
                        if (val := abs(current.bottom() - other.top())) <= y_dist:
                            y_dist = val
                            y_mode = 0
                            y_rect = other

                        if (val := abs(other.bottom() - current.top())) <= y_dist:
                            y_dist = val
                            y_mode = 1
                            y_rect = other

            if x_rect and x_dist < dist:
                if x_mode == 0:
                    point.setX(x_rect.left() - current.width())
                else:
                    point.setX(x_rect.right())

                if abs(current.top() - x_rect.top()) <= dist:
                    point.setY(x_rect.top())

                elif abs(current.bottom() - x_rect.bottom()) <= dist:
                    point.setY(x_rect.bottom() - current.height())

            if y_rect and y_dist < dist:
                if y_mode == 0:
                    point.setY(y_rect.top() - current.height())
                else:
                    point.setY(y_rect.bottom())

                if abs(current.left() - y_rect.left()) <= dist:
                    point.setX(y_rect.left())

                elif abs(current.right() - y_rect.right()) <= dist:
                    point.setX(y_rect.right() - current.width())

            return point

        return super(PreviewItem, self).itemChange(change, value)
