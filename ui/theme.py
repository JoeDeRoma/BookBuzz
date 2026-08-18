import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import (
    QFont, QFontDatabase, QPixmap, QImage, QPainter, QColor, QIcon, QPen, QBrush
)
from PySide6.QtWidgets import QApplication


def get_base_path() -> Path:
    """Returns base directory for bundled PyInstaller or development environment."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.resolve()


def get_asset_path(*relative_parts: str) -> Path:
    return get_base_path() / "assets" / Path(*relative_parts)


class Colors:
    # Book Buzz — Warm Natural Palette
    BG_CREAM = QColor("#f6f0df")
    BG_PARCHMENT = QColor("#ebdcb9")
    BG_DARK_PARCHMENT = QColor("#dfc89f")
    BG_CARD = QColor("#fffdf7")
    
    TEXT_DARK = QColor("#38271d")
    TEXT_MUTED = QColor("#755845")
    TEXT_LIGHT = QColor("#fbf7ee")
    
    BORDER_DARK = QColor("#543d2b")
    BORDER_LIGHT = QColor("#856549")
    BORDER_FOCUS = QColor("#a65b2d")
    
    ACCENT_GREEN = QColor("#5c8b39")
    ACCENT_GREEN_HOVER = QColor("#72a847")
    ACCENT_GREEN_BG = QColor("#e3eed5")
    
    ACCENT_RED = QColor("#c94a3a")
    ACCENT_RED_HOVER = QColor("#df5a48")
    ACCENT_RED_BG = QColor("#fbe7e4")
    
    ACCENT_GOLD = QColor("#d99621")
    ACCENT_GOLD_HOVER = QColor("#efad32")
    ACCENT_GOLD_BG = QColor("#fdf3d9")
    
    ACCENT_BLUE = QColor("#3f7cb5")
    ACCENT_BLUE_BG = QColor("#e1eef9")
    
    SHADOW = QColor(64, 47, 35, 40)


class ThemeManager:
    _instance = None

    def __init__(self):
        self.font_family = "Segoe UI"
        self.pixel_font_loaded = False
        self._pixmap_cache: Dict[str, QPixmap] = {}
        self._init_fonts()

    @classmethod
    def instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def _init_fonts(self):
        font_path = get_asset_path("ui", "fonts", "pixelFont-7-8x14-bookbuzz.ttf")
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    self.font_family = families[0]
                    self.pixel_font_loaded = True
                    return
        # Fallback fonts
        self.font_family = "Segoe UI"

    def get_font(self, size: int = 12, bold: bool = False) -> QFont:
        font = QFont(self.font_family, size)
        font.setBold(bold)
        return font

    def get_pixmap(self, relative_path: str) -> QPixmap:
        if relative_path not in self._pixmap_cache:
            full_path = get_asset_path(*relative_path.split("/"))
            if full_path.exists():
                self._pixmap_cache[relative_path] = QPixmap(str(full_path))
            else:
                self._pixmap_cache[relative_path] = QPixmap()
        return self._pixmap_cache[relative_path]

    def slice_sprite(
        self,
        relative_path: str,
        x: int,
        y: int,
        w: int,
        h: int,
        scale: int = 1
    ) -> QPixmap:
        full_pixmap = self.get_pixmap(relative_path)
        if full_pixmap.isNull():
            return QPixmap()
        cropped = full_pixmap.copy(x, y, w, h)
        if scale > 1:
            return cropped.scaled(
                w * scale,
                h * scale,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
        return cropped

    def get_chicken_idle_frames(self, scale: int = 2) -> List[QPixmap]:
        """Returns 4 frames of idle chicken animation."""
        frames = []
        for i in range(4):
            frames.append(
                self.slice_sprite("sprites/Characters/Free Chicken Sprites.png", i * 16, 0, 16, 16, scale=scale)
            )
        return frames

    def get_chicken_peck_frames(self, scale: int = 2) -> List[QPixmap]:
        """Returns 4 frames of pecking chicken animation."""
        frames = []
        for i in range(4):
            frames.append(
                self.slice_sprite("sprites/Characters/Free Chicken Sprites.png", i * 16, 16, 16, 16, scale=scale)
            )
        return frames

    def get_cow_idle_frames(self, scale: int = 2) -> List[QPixmap]:
        """Returns 3 frames of idle cow animation."""
        frames = []
        for i in range(3):
            frames.append(
                self.slice_sprite("sprites/Characters/Free Cow Sprites.png", i * 32, 0, 32, 32, scale=scale)
            )
        return frames

    def get_character_idle_frames(self, scale: int = 2) -> List[QPixmap]:
        """Returns 4 frames of idle farmer character animation."""
        frames = []
        for i in range(4):
            frames.append(
                self.slice_sprite("sprites/Characters/Basic Charakter Spritesheet.png", i * 48, 0, 48, 48, scale=scale)
            )
        return frames

    def draw_panel(
        self,
        painter: QPainter,
        rect: QRect,
        bg_color: QColor = None,
        border_color: QColor = None,
        border_width: int = 2,
        radius: int = 6
    ):
        """Draws a clean rounded-rectangle panel — replaces the old warped 9-patch."""
        if bg_color is None:
            bg_color = Colors.BG_PARCHMENT
        if border_color is None:
            border_color = Colors.BORDER_DARK

        r = rect.adjusted(1, 1, -2, -2)

        # Subtle drop shadow
        shadow_r = r.translated(2, 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Colors.SHADOW))
        painter.drawRoundedRect(shadow_r, radius, radius)

        # Background fill
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(r, radius, radius)


def get_app_stylesheet() -> str:
    return """
    QWidget {
        background-color: transparent;
        color: #38271d;
        font-family: "Segoe UI", sans-serif;
        font-size: 13px;
    }

    QMainWindow {
        background-color: #f4ecda;
    }

    QScrollArea {
        background-color: transparent;
        border: none;
    }

    QScrollBar:vertical {
        border: 2px solid #543d2b;
        background: #ebdcb9;
        width: 16px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #856549;
        min-height: 20px;
        border: 1px solid #543d2b;
    }
    QScrollBar::handle:vertical:hover {
        background: #a65b2d;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        border: 2px solid #543d2b;
        background: #ebdcb9;
        height: 16px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background: #856549;
        min-width: 20px;
        border: 1px solid #543d2b;
    }
    QScrollBar::handle:horizontal:hover {
        background: #a65b2d;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Tab Widget */
    QTabWidget::pane {
        border: 3px solid #543d2b;
        background-color: #ebdcb9;
        top: -3px;
        border-radius: 4px;
    }

    QTabBar::tab {
        background-color: #dfc89f;
        color: #543d2b;
        border: 3px solid #543d2b;
        border-bottom: none;
        padding: 8px 18px;
        margin-right: 4px;
        font-weight: bold;
        font-size: 13px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }

    QTabBar::tab:selected {
        background-color: #ebdcb9;
        color: #38271d;
        border-bottom: 3px solid #ebdcb9;
        padding-bottom: 9px;
    }

    QTabBar::tab:hover:!selected {
        background-color: #eeddbb;
    }

    /* Tables */
    QTableWidget {
        background-color: #fffdf7;
        gridline-color: #dfc89f;
        border: 2px solid #543d2b;
        border-radius: 4px;
        selection-background-color: #e3eed5;
        selection-color: #38271d;
    }

    QHeaderView::section {
        background-color: #dfc89f;
        color: #38271d;
        padding: 6px;
        border: 1px solid #543d2b;
        font-weight: bold;
    }

    /* Input & Combobox */
    QLineEdit {
        background-color: #fffdf7;
        color: #38271d;
        border: 2px solid #543d2b;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 13px;
    }

    QLineEdit:focus {
        border: 2px solid #a65b2d;
    }

    /* Checkbox */
    QCheckBox {
        spacing: 8px;
        font-size: 13px;
        color: #38271d;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #543d2b;
        background-color: #fffdf7;
        border-radius: 3px;
    }

    QCheckBox::indicator:checked {
        background-color: #5c8b39;
        border: 2px solid #38271d;
        image: none;
    }

    QCheckBox::indicator:hover {
        border-color: #a65b2d;
    }

    /* Tooltip */
    QToolTip {
        background-color: #fffdf7;
        color: #38271d;
        border: 2px solid #543d2b;
        padding: 4px 8px;
        font-size: 12px;
    }
    """
