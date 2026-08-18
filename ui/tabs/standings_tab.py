from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from engine.ranked_pairs import RankedPairsResult
from ui.theme import ThemeManager, Colors
from ui.widgets.retro_frame import RetroFrame, RetroCard
from ui.widgets.animated_sprite import AnimatedSpriteWidget


class StandingsTab(QWidget):
    """
    Winner & Full Standings tab.
    Displays crowned winner card with cute animations, plus detailed standings leaderboard
    with RP scores and head-to-head defeat margin notes.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.result: Optional[RankedPairsResult] = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(4, 4, 4, 4)
        self.container_layout.setSpacing(12)

        # --- Top Winner Banner ---
        self.winner_frame = RetroFrame(
            container,
            pixmap_key="ui/Sprite sheets/Dialouge UI/dialog box.png",
            corner_size=16,
            dest_corner_size=16,
            content_margins=(18, 16, 18, 16)
        )
        winner_layout = QHBoxLayout(self.winner_frame)
        winner_layout.setSpacing(16)

        # Animated farmer character
        self.farmer_sprite = AnimatedSpriteWidget.create_character(scale=2, parent=self.winner_frame)
        winner_layout.addWidget(self.farmer_sprite)

        winner_info = QVBoxLayout()
        winner_info.setSpacing(4)
        
        self.lbl_winner_tag = QLabel("👑 BOOK CLUB WINNER (RANKED PAIRS)")
        self.lbl_winner_tag.setFont(ThemeManager.instance().get_font(11, bold=True))
        self.lbl_winner_tag.setStyleSheet(f"color: {Colors.ACCENT_GOLD.name()};")
        winner_info.addWidget(self.lbl_winner_tag)

        self.lbl_winner_title = QLabel("Run analysis to reveal winner!")
        self.lbl_winner_title.setFont(ThemeManager.instance().get_font(17, bold=True))
        self.lbl_winner_title.setStyleSheet(f"color: {Colors.TEXT_DARK.name()};")
        self.lbl_winner_title.setWordWrap(True)
        winner_info.addWidget(self.lbl_winner_title)

        self.lbl_winner_stats = QLabel("Based on 0 ballots.")
        self.lbl_winner_stats.setFont(ThemeManager.instance().get_font(10))
        self.lbl_winner_stats.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()};")
        winner_info.addWidget(self.lbl_winner_stats)

        winner_layout.addLayout(winner_info, stretch=1)

        # Cute cow mascot on the right
        self.cow_sprite = AnimatedSpriteWidget.create_cow(scale=2, parent=self.winner_frame)
        winner_layout.addWidget(self.cow_sprite)

        self.container_layout.addWidget(self.winner_frame)

        # --- Leaderboard Header ---
        self.leaderboard_card = RetroCard(title="OFFICIAL LEADERBOARD & HEAD-TO-HEAD MARGINS", parent=container)
        self.leaderboard_layout = QVBoxLayout()
        self.leaderboard_layout.setSpacing(8)
        self.leaderboard_card.set_content_layout(self.leaderboard_layout)
        self.container_layout.addWidget(self.leaderboard_card)

        self.container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def display_results(self, result: RankedPairsResult):
        self.result = result
        
        # 1. Update Winner Card
        self.lbl_winner_title.setText(result.winner_name)
        self.lbl_winner_stats.setText(
            f"Calculated with {result.included_ballots_count} active ballots ({result.excluded_ballots_count} excluded) across {result.num_candidates} candidates."
        )

        # 2. Clear previous leaderboard items
        while self.leaderboard_layout.count():
            item = self.leaderboard_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 3. Populate Standings Cards
        for item in result.standings:
            card = self._create_standing_card(item)
            self.leaderboard_layout.addWidget(card)

    def _create_standing_card(self, standing) -> QWidget:
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        # Top row: Rank badge + Book Names + Score
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Rank badge
        lbl_rank = QLabel(f"#{standing.rank}")
        lbl_rank.setFont(ThemeManager.instance().get_font(13, bold=True))
        lbl_rank.setFixedWidth(42)
        lbl_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if standing.rank == 1:
            lbl_rank.setStyleSheet(f"background-color: {Colors.ACCENT_GOLD.name()}; color: {Colors.TEXT_DARK.name()}; border: 1px solid {Colors.BORDER_DARK.name()}; border-radius: 3px; padding: 3px;")
        elif standing.rank == 2:
            lbl_rank.setStyleSheet(f"background-color: #d8dee8; color: {Colors.TEXT_DARK.name()}; border: 1px solid {Colors.BORDER_DARK.name()}; border-radius: 3px; padding: 3px;")
        elif standing.rank == 3:
            lbl_rank.setStyleSheet(f"background-color: #dfb28b; color: {Colors.TEXT_DARK.name()}; border: 1px solid {Colors.BORDER_DARK.name()}; border-radius: 3px; padding: 3px;")
        else:
            lbl_rank.setStyleSheet(f"background-color: {Colors.BG_DARK_PARCHMENT.name()}; color: {Colors.TEXT_DARK.name()}; border: 1px solid {Colors.BORDER_DARK.name()}; border-radius: 3px; padding: 3px;")

        top_row.addWidget(lbl_rank)

        # Book Title(s)
        title_text = " (Tie) " + ", ".join(standing.candidates) if standing.is_tie else standing.candidates[0]
        lbl_title = QLabel(title_text)
        lbl_title.setFont(ThemeManager.instance().get_font(13, bold=True))
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_DARK.name()};")
        lbl_title.setWordWrap(True)
        top_row.addWidget(lbl_title, stretch=1)

        # RP Score Tag
        lbl_score = QLabel(f"RP Score: {standing.score}")
        lbl_score.setFont(ThemeManager.instance().get_font(10, bold=True))
        lbl_score.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()}; background-color: {Colors.BG_CREAM.name()}; border: 1px solid {Colors.BORDER_LIGHT.name()}; border-radius: 3px; padding: 4px 8px;")
        lbl_score.setToolTip("Number of candidates strictly reachable in the locked Ranked Pairs victory graph.")
        top_row.addWidget(lbl_score)

        card_layout.addLayout(top_row)

        # Defeat Notes vs previous rank candidates
        if standing.defeat_notes:
            notes_box = QVBoxLayout()
            notes_box.setContentsMargins(52, 2, 6, 2)
            notes_box.setSpacing(2)
            for note in standing.defeat_notes:
                lbl_note = QLabel(f"↳ {note}")
                lbl_note.setFont(ThemeManager.instance().get_font(10))
                lbl_note.setStyleSheet(f"color: {Colors.ACCENT_RED.name() if 'Lost' in note else Colors.TEXT_MUTED.name()};")
                notes_box.addWidget(lbl_note)
            card_layout.addLayout(notes_box)

        card.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD.name()};
                border: 1px solid {Colors.BORDER_LIGHT.name()};
                border-radius: 3px;
            }}
        """)
        return card
