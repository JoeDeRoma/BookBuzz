from typing import List, Optional
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QPaintEvent, QColor, QPen
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from ui.theme import ThemeManager, Colors


class ComplianceBadge(QWidget):
    """
    A cute pixel-art compliance tag showing Valid (Sprout) or Non-Compliant (Warning).
    """
    def __init__(
        self,
        is_compliant: bool,
        issues: Optional[List[str]] = None,
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.is_compliant = is_compliant
        self.issues = issues or []
        self.setFixedHeight(26)
        
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        self.label = QLabel()
        self.label.setFont(ThemeManager.instance().get_font(10, bold=True))
        
        if self.is_compliant:
            self.label.setText("✔ COMPLIANT")
            self.label.setStyleSheet(f"color: {Colors.ACCENT_GREEN.name()};")
            self.setToolTip("This ballot meets all voting rules (>= 5 ranked, sequential starting at 1).")
        else:
            issue_summary = self.issues[0] if self.issues else "Non-compliant"
            if len(self.issues) > 1:
                display_text = f"⚠ {issue_summary} (+{len(self.issues) - 1} more)"
            else:
                display_text = f"⚠ {issue_summary}"
            self.label.setText(display_text)
            self.label.setStyleSheet(f"color: {Colors.ACCENT_RED.name()};")
            self.setToolTip("Issues detected:\n• " + "\n• ".join(self.issues))

        layout.addWidget(self.label)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        rect = self.rect().adjusted(1, 1, -2, -2)
        bg = Colors.ACCENT_GREEN_BG if self.is_compliant else Colors.ACCENT_RED_BG
        border = Colors.ACCENT_GREEN if self.is_compliant else Colors.ACCENT_RED
        
        painter.fillRect(rect, bg)
        painter.setPen(QPen(border, 2))
        painter.drawRect(rect)
