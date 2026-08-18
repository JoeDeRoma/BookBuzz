from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QPen, QFont, QMouseEvent, QFontMetrics
from PySide6.QtWidgets import QPushButton, QWidget
from ui.theme import ThemeManager, Colors


class PixelButton(QPushButton):
    """
    A custom pixel-art styled push button with crisp retro borders,
    hover glow, and satisfying tactile press-down depression.
    """
    def __init__(
        self,
        text: str = "",
        variant: str = "parchment",  # "parchment", "green", "red", "gold", "blue"
        font_size: int = 11,
        parent: QWidget = None
    ):
        super().__init__(text, parent)
        self.variant = variant
        self.font_size = font_size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(32)
        self._is_pressed = False
        self._is_hovered = False

    def sizeHint(self) -> QSize:
        font = ThemeManager.instance().get_font(self.font_size, bold=True)
        fm = QFontMetrics(font)
        text_w = fm.horizontalAdvance(self.text())
        icon_w = self.iconSize().width() + 6 if not self.icon().isNull() else 0
        w = max(70, text_w + icon_w + 24)
        return QSize(w, 32)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def _get_colors(self):
        if self.variant == "green":
            bg = Colors.ACCENT_GREEN_HOVER if self._is_hovered else Colors.ACCENT_GREEN
            text_color = Colors.TEXT_LIGHT
            border = Colors.BORDER_DARK
            shadow = QColor("#3b5a24")
        elif self.variant == "red":
            bg = Colors.ACCENT_RED_HOVER if self._is_hovered else Colors.ACCENT_RED
            text_color = Colors.TEXT_LIGHT
            border = Colors.BORDER_DARK
            shadow = QColor("#7a2b22")
        elif self.variant == "gold":
            bg = Colors.ACCENT_GOLD_HOVER if self._is_hovered else Colors.ACCENT_GOLD
            text_color = Colors.TEXT_DARK
            border = Colors.BORDER_DARK
            shadow = QColor("#8c5e12")
        elif self.variant == "blue":
            bg = QColor("#4e8fcb") if self._is_hovered else Colors.ACCENT_BLUE
            text_color = Colors.TEXT_LIGHT
            border = Colors.BORDER_DARK
            shadow = QColor("#28527a")
        else:  # parchment
            bg = QColor("#f4e4c3") if self._is_hovered else Colors.BG_PARCHMENT
            text_color = Colors.TEXT_DARK
            border = Colors.BORDER_DARK
            shadow = Colors.BG_DARK_PARCHMENT

        if not self.isEnabled():
            bg = QColor("#d0c4af")
            text_color = QColor("#8a7c6a")
            border = QColor("#8a7c6a")
            shadow = QColor("#b5a894")

        return bg, text_color, border, shadow

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        bg_col, text_col, border_col, shadow_col = self._get_colors()
        
        w = self.width()
        h = self.height()
        
        offset = 2 if self._is_pressed else 0
        btn_rect = QRect(1, 1 + offset, w - 2, h - 3 - (0 if self._is_pressed else 2))
        
        # Draw bottom shadow if not pressed
        if not self._is_pressed and self.isEnabled():
            painter.fillRect(QRect(1, h - 3, w - 2, 2), shadow_col)
            
        # Draw button face
        painter.fillRect(btn_rect, bg_col)
        
        # Draw pixel border
        painter.setPen(QPen(border_col, 2))
        painter.drawRect(btn_rect)

        # Draw icon & text
        painter.setPen(text_col)
        painter.setFont(ThemeManager.instance().get_font(self.font_size, bold=True))
        
        icon = self.icon()
        text = self.text()
        
        if not icon.isNull():
            icon_size = self.iconSize()
            if not icon_size.isValid():
                icon_size = QSize(16, 16)
            total_content_w = icon_size.width() + 6 + painter.fontMetrics().horizontalAdvance(text)
            start_x = max(6, (w - total_content_w) // 2)
            icon_y = (btn_rect.height() - icon_size.height()) // 2 + offset + 1
            icon.paint(painter, start_x, icon_y, icon_size.width(), icon_size.height())
            text_rect = QRect(start_x + icon_size.width() + 6, offset, w - (start_x + icon_size.width() + 6) - 4, btn_rect.height())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        else:
            text_rect = QRect(2, offset, w - 4, btn_rect.height())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
