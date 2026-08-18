from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QScrollArea
)
from engine.ballot_parser import Ballot
from ui.theme import ThemeManager, Colors
from ui.widgets.retro_frame import RetroFrame, RetroCard
from ui.widgets.pixel_button import PixelButton
from ui.widgets.status_badge import ComplianceBadge
from ui.widgets.animated_sprite import AnimatedSpriteWidget


class BallotDetailDialog(QDialog):
    """
    Cute pixel-art modal dialog showing the complete ballot submission for an individual voter,
    highlighting rankings, unranked candidates, and compliance issues.
    """
    inclusion_toggled = Signal(bool)

    def __init__(self, ballot: Ballot, parent: QWidget = None):
        super().__init__(parent)
        self.ballot = ballot
        self.setWindowTitle(f"Ballot: {ballot.voter_name}")
        self.resize(560, 620)
        self.setStyleSheet(ThemeManager.instance().get_font().family())

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)

        # Retro 9-patch frame container
        frame = RetroFrame(self, pixmap_key="ui/Sprite sheets/Dialouge UI/dialog box.png", corner_size=16, dest_corner_size=16, content_margins=(20, 20, 20, 20))
        root_layout.addWidget(frame)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(14)

        # --- Top Header ---
        header_layout = QHBoxLayout()
        
        avatar = AnimatedSpriteWidget.create_character(scale=2, parent=self)
        header_layout.addWidget(avatar)

        title_info = QVBoxLayout()
        lbl_name = QLabel(self.ballot.voter_name)
        lbl_name.setFont(ThemeManager.instance().get_font(16, bold=True))
        lbl_name.setStyleSheet(f"color: {Colors.TEXT_DARK.name()};")
        title_info.addWidget(lbl_name)

        if self.ballot.timestamp:
            lbl_time = QLabel(f"Submitted: {self.ballot.timestamp}")
            lbl_time.setFont(ThemeManager.instance().get_font(10))
            lbl_time.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()};")
            title_info.addWidget(lbl_time)

        header_layout.addLayout(title_info)
        header_layout.addStretch()
        
        # Compliance Tag
        badge = ComplianceBadge(self.ballot.is_compliant, self.ballot.issues, parent=self)
        header_layout.addWidget(badge)

        frame_layout.addLayout(header_layout)

        # --- Issues / Compliance Breakdown Box ---
        if not self.ballot.is_compliant:
            issues_card = RetroCard(
                title="⚠ COMPLIANCE ISSUES DETECTED",
                bg_color=Colors.ACCENT_RED_BG,
                border_color=Colors.ACCENT_RED,
                parent=self
            )
            issues_box = QVBoxLayout()
            issues_box.setSpacing(4)
            for issue in self.ballot.issues:
                lbl_issue = QLabel(f"• {issue}")
                lbl_issue.setFont(ThemeManager.instance().get_font(11, bold=True))
                lbl_issue.setStyleSheet(f"color: {Colors.ACCENT_RED.name()};")
                issues_box.addWidget(lbl_issue)
            issues_card.set_content_layout(issues_box)
            frame_layout.addWidget(issues_card)
        else:
            ok_card = RetroCard(
                title="✔ VALID BALLOT",
                bg_color=Colors.ACCENT_GREEN_BG,
                border_color=Colors.ACCENT_GREEN,
                parent=self
            )
            ok_box = QVBoxLayout()
            lbl_ok = QLabel("• Ranked 5 or more books\n• Sequential order starting at 1\n• No duplicate or skipped ranks")
            lbl_ok.setFont(ThemeManager.instance().get_font(10))
            lbl_ok.setStyleSheet(f"color: {Colors.ACCENT_GREEN.name()};")
            ok_box.addWidget(lbl_ok)
            ok_card.set_content_layout(ok_box)
            frame_layout.addWidget(ok_card)

        # --- Ranked Books Table ---
        rankings_card = RetroCard(title=f"VOTER RANKINGS ({self.ballot.num_ranked} Ranked Books)", parent=self)
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Rank", "Book Title"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Fill table with ranked candidates
        all_display_items = []
        for rank_num, book_title in self.ballot.sorted_ranks:
            all_display_items.append((str(rank_num), book_title, True))

        for unranked_book in self.ballot.unranked_books:
            all_display_items.append(("Unranked", unranked_book, False))

        self.table.setRowCount(len(all_display_items))
        for row_idx, (rank_str, title_str, is_ranked) in enumerate(all_display_items):
            item_rank = QTableWidgetItem(rank_str)
            item_rank.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_title = QTableWidgetItem(title_str)

            if is_ranked:
                item_rank.setFont(ThemeManager.instance().get_font(11, bold=True))
                item_title.setFont(ThemeManager.instance().get_font(11))
            else:
                item_rank.setFont(ThemeManager.instance().get_font(10))
                item_rank.setForeground(Colors.TEXT_MUTED)
                item_title.setFont(ThemeManager.instance().get_font(10))
                item_title.setForeground(Colors.TEXT_MUTED)

            self.table.setItem(row_idx, 0, item_rank)
            self.table.setItem(row_idx, 1, item_title)

        table_layout.addWidget(self.table)
        rankings_card.set_content_layout(table_layout)
        frame_layout.addWidget(rankings_card)

        # --- Bottom Bar (Inclusion Toggle & Close Button) ---
        bottom_layout = QHBoxLayout()
        
        self.chk_include = QCheckBox("Include this ballot in final analysis")
        self.chk_include.setChecked(self.ballot.included)
        self.chk_include.setFont(ThemeManager.instance().get_font(11, bold=True))
        self.chk_include.toggled.connect(self._on_toggle_inclusion)
        bottom_layout.addWidget(self.chk_include)

        bottom_layout.addStretch()

        btn_close = PixelButton("Close", variant="parchment", parent=self)
        btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(btn_close)

        frame_layout.addLayout(bottom_layout)

    def _on_toggle_inclusion(self, checked: bool):
        self.ballot.included = checked
        self.inclusion_toggled.emit(checked)
