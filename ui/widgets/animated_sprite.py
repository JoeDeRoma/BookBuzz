from typing import List, Optional
from PySide6.QtCore import Qt, QTimer, QSize, QRect
from PySide6.QtGui import QPainter, QPixmap, QPaintEvent
from PySide6.QtWidgets import QWidget
from ui.theme import ThemeManager


class AnimatedSpriteWidget(QWidget):
    """
    A widget that smoothly renders animated sprite sequences from the Book Buzz sheets.
    """
    def __init__(
        self,
        frames: Optional[List[QPixmap]] = None,
        frame_rate_ms: int = 200,
        scale: int = 2,
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.frames = frames or []
        self.current_frame_idx = 0
        self.frame_rate_ms = frame_rate_ms
        self.scale = scale
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        
        if self.frames:
            self._update_size()
            self.timer.start(self.frame_rate_ms)

    def set_frames(self, frames: List[QPixmap], frame_rate_ms: Optional[int] = None):
        self.frames = frames
        self.current_frame_idx = 0
        if frame_rate_ms:
            self.frame_rate_ms = frame_rate_ms
        self._update_size()
        if self.frames and not self.timer.isActive():
            self.timer.start(self.frame_rate_ms)
        self.update()

    def _update_size():
        pass

    def _update_size(self):
        if self.frames and not self.frames[0].isNull():
            w = self.frames[0].width()
            h = self.frames[0].height()
            self.setFixedSize(w, h)

    def _next_frame(self):
        if not self.frames:
            return
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if not self.frames or self.current_frame_idx >= len(self.frames):
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        current_pixmap = self.frames[self.current_frame_idx]
        if not current_pixmap.isNull():
            painter.drawPixmap(0, 0, current_pixmap)

    @classmethod
    def create_chicken(cls, pecking: bool = False, scale: int = 2, parent: QWidget = None) -> 'AnimatedSpriteWidget':
        theme = ThemeManager.instance()
        frames = theme.get_chicken_peck_frames(scale=scale) if pecking else theme.get_chicken_idle_frames(scale=scale)
        return cls(frames=frames, frame_rate_ms=250, scale=scale, parent=parent)

    @classmethod
    def create_cow(cls, scale: int = 2, parent: QWidget = None) -> 'AnimatedSpriteWidget':
        theme = ThemeManager.instance()
        frames = theme.get_cow_idle_frames(scale=scale)
        return cls(frames=frames, frame_rate_ms=400, scale=scale, parent=parent)

    @classmethod
    def create_character(cls, scale: int = 2, parent: QWidget = None) -> 'AnimatedSpriteWidget':
        theme = ThemeManager.instance()
        frames = theme.get_character_idle_frames(scale=scale)
        return cls(frames=frames, frame_rate_ms=200, scale=scale, parent=parent)
