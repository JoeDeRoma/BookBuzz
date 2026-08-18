from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QPen, QBrush
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from ui.theme import ThemeManager, Colors


class RetroFrame(QFrame):
    """
    A QFrame that paints a clean rounded-rectangle panel with a subtle shadow.
    Replaces the old warped 9-patch approach.
    """
    def __init__(
        self,
        parent: QWidget = None,
        pixmap_key: str = "",
        corner_size: int = 16,
        dest_corner_size: int = 16,
        content_margins: tuple = (16, 16, 16, 16),
        bg_color: QColor = None,
        border_color: QColor = None,
    ):
        super().__init__(parent)
        self.bg_color = bg_color or Colors.BG_PARCHMENT
        self.border_color = border_color or Colors.BORDER_DARK
        self.setContentsMargins(*content_margins)
        self.theme = ThemeManager.instance()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.theme.draw_panel(
            painter,
            self.rect(),
            bg_color=self.bg_color,
            border_color=self.border_color,
        )


class RetroCard(QWidget):
    """
    A clean card panel with an optional header.
    """
    def __init__(
        self,
        title: str = "",
        parent: QWidget = None,
        bg_color: QColor = Colors.BG_CARD,
        border_color: QColor = Colors.BORDER_DARK
    ):
        super().__init__(parent)
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)

        if title:
            self.header_label = QLabel(title)
            self.header_label.setFont(ThemeManager.instance().get_font(12, bold=True))
            self.header_label.setStyleSheet(f"color: {Colors.TEXT_DARK.name()};")
            self.main_layout.addWidget(self.header_label)

    def set_content_layout(self, layout):
        self.main_layout.addLayout(layout)

    def add_widget(self, widget: QWidget):
        self.main_layout.addWidget(widget)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rect = self.rect().adjusted(1, 1, -2, -2)
        
        # Shadow
        shadow_rect = rect.translated(2, 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Colors.SHADOW))
        painter.drawRoundedRect(shadow_rect, 6, 6)
        
        # Background
        painter.setBrush(QBrush(self.bg_color))
        painter.setPen(QPen(self.border_color, 2))
        painter.drawRoundedRect(rect, 6, 6)


class PixelStatCard(QWidget):
    """
    A compact stat card showing a metric number, title, and optional subtitle.
    """
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        accent_color: QColor = Colors.ACCENT_GREEN,
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.accent_color = accent_color
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(ThemeManager.instance().get_font(10, bold=True))
        self.lbl_title.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()};")
        layout.addWidget(self.lbl_title)
        
        self.lbl_val = QLabel(value)
        self.lbl_val.setFont(ThemeManager.instance().get_font(18, bold=True))
        self.lbl_val.setStyleSheet(f"color: {accent_color.name()};")
        layout.addWidget(self.lbl_val)
        
        if subtitle:
            self.lbl_sub = QLabel(subtitle)
            self.lbl_sub.setFont(ThemeManager.instance().get_font(9))
            self.lbl_sub.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()};")
            layout.addWidget(self.lbl_sub)
        else:
            self.lbl_sub = None

    def update_value(self, value: str, subtitle: str = ""):
        self.lbl_val.setText(value)
        if self.lbl_sub and subtitle:
            self.lbl_sub.setText(subtitle)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rect = self.rect().adjusted(1, 1, -2, -2)
        
        # Shadow
        shadow_rect = rect.translated(2, 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Colors.SHADOW))
        painter.drawRoundedRect(shadow_rect, 4, 4)

        # Background
        painter.setBrush(QBrush(Colors.BG_CARD))
        painter.setPen(QPen(Colors.BORDER_DARK, 2))
        painter.drawRoundedRect(rect, 4, 4)

        # Left accent bar
        bar_rect = QRect(rect.x(), rect.y(), 5, rect.height())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.accent_color))
        painter.drawRoundedRect(bar_rect, 2, 2)
