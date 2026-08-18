from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame
)
from engine.ranked_pairs import RankedPairsResult
from ui.theme import ThemeManager, Colors
from ui.widgets.retro_frame import RetroCard


class MatrixTab(QWidget):
    """
    Pairwise Head-to-Head Matchup Matrix tab.
    Displays a color-coded matrix of every candidate vs candidate comparison.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.result: Optional[RankedPairsResult] = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Main Table Card
        card = RetroCard(title="HEAD-TO-HEAD PAIRWISE VICTORY MATRIX (Row vs Column)", parent=self)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.cellClicked.connect(self._on_cell_clicked)
        card_layout.addWidget(self.table)

        # Matchup Details Strip
        self.lbl_details = QLabel("Click any cell in the matrix to view the head-to-head matchup breakdown.")
        self.lbl_details.setFont(ThemeManager.instance().get_font(11))
        self.lbl_details.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()}; padding: 8px; background-color: {Colors.BG_CREAM.name()}; border: 1px solid {Colors.BORDER_LIGHT.name()}; border-radius: 3px;")
        card_layout.addWidget(self.lbl_details)

        card.set_content_layout(card_layout)
        main_layout.addWidget(card)

    def display_results(self, result: RankedPairsResult):
        self.result = result
        cands = result.candidates
        n = len(cands)

        self.table.setRowCount(n)
        self.table.setColumnCount(n)
        
        # Format candidate headers cleanly
        col_headers = [f"#{i+1}\n{c[:11]}.." if len(c) > 13 else f"#{i+1}\n{c}" for i, c in enumerate(cands)]
        row_headers = [f"#{i+1} {c}" for i, c in enumerate(cands)]
        
        self.table.setHorizontalHeaderLabels(col_headers)
        self.table.setVerticalHeaderLabels(row_headers)

        self.table.horizontalHeader().setDefaultSectionSize(95)
        for i in range(n):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            self.table.setRowHeight(i, 48)

        matrix = result.pairwise_matrix

        for i in range(n):
            for j in range(n):
                if i == j:
                    item = QTableWidgetItem("—")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(QBrush(QColor("#e8ded0")))
                    item.setForeground(QBrush(Colors.TEXT_MUTED))
                    self.table.setItem(i, j, item)
                    continue

                v_for = matrix[i, j]
                v_against = matrix[j, i]
                margin = v_for - v_against

                if margin > 0:
                    text = f"+{margin:g}\n({v_for:g} vs {v_against:g})"
                    bg = Colors.ACCENT_GREEN_BG
                    fg = Colors.ACCENT_GREEN
                elif margin < 0:
                    text = f"{margin:g}\n({v_for:g} vs {v_against:g})"
                    bg = Colors.ACCENT_RED_BG
                    fg = Colors.ACCENT_RED
                else:
                    text = f"0\n({v_for:g} vs {v_against:g})"
                    bg = Colors.ACCENT_GOLD_BG
                    fg = Colors.ACCENT_GOLD

                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(ThemeManager.instance().get_font(9, bold=True))
                item.setBackground(QBrush(bg))
                item.setForeground(QBrush(fg))
                item.setToolTip(f"Row '{cands[i]}' vs Column '{cands[j]}': {v_for:g} to {v_against:g} (Margin: {margin:+g})")
                self.table.setItem(i, j, item)

    def _on_cell_clicked(self, row: int, col: int):
        if not self.result or row == col:
            return
        cands = self.result.candidates
        cand_a = cands[row]
        cand_b = cands[col]
        v_a = self.result.pairwise_matrix[row, col]
        v_b = self.result.pairwise_matrix[col, row]
        diff = v_a - v_b

        if diff > 0:
            outcome = f"✔ '{cand_a}' WINS over '{cand_b}' by {diff:g} votes ({v_a:g} vs {v_b:g})"
            color = Colors.ACCENT_GREEN.name()
        elif diff < 0:
            outcome = f"✖ '{cand_a}' LOSES to '{cand_b}' by {-diff:g} votes ({v_a:g} vs {v_b:g})"
            color = Colors.ACCENT_RED.name()
        else:
            outcome = f"🤝 '{cand_a}' TIED with '{cand_b}' ({v_a:g} vs {v_b:g})"
            color = Colors.ACCENT_GOLD.name()

        self.lbl_details.setText(f"Matchup: {outcome}")
        self.lbl_details.setStyleSheet(f"color: {color}; font-weight: bold; padding: 8px; background-color: {Colors.BG_CREAM.name()}; border: 1px solid {Colors.BORDER_LIGHT.name()}; border-radius: 3px;")
