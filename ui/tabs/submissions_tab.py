from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QLineEdit
)
from engine.ballot_parser import BallotDataset, Ballot
from ui.theme import ThemeManager, Colors
from ui.widgets.retro_frame import RetroCard, PixelStatCard
from ui.widgets.pixel_button import PixelButton
from ui.widgets.status_badge import ComplianceBadge
from ui.widgets.animated_sprite import AnimatedSpriteWidget
from ui.dialogs.ballot_detail_dialog import BallotDetailDialog


class SubmissionsTab(QWidget):
    """
    Submissions & Compliance inspection tab.
    Allows viewing every ballot, inspecting individual voter choices,
    viewing compliance diagnostic tags, and checking/unchecking ballots.
    """
    calculation_requested = Signal()
    ballot_selection_changed = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.dataset: Optional[BallotDataset] = None
        self._row_to_ballot: dict[int, Ballot] = {}
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # --- 1. Top Stat Cards Bar ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)

        self.stat_total = PixelStatCard("Total Ballots", "0", "All submissions", accent_color=Colors.BORDER_LIGHT, parent=self)
        self.stat_compliant = PixelStatCard("Compliant", "0", "Meet all rules", accent_color=Colors.ACCENT_GREEN, parent=self)
        self.stat_non_compliant = PixelStatCard("Non-Compliant", "0", "Rule violations", accent_color=Colors.ACCENT_RED, parent=self)
        self.stat_included = PixelStatCard("Included in Run", "0", "Counted for results", accent_color=Colors.ACCENT_BLUE, parent=self)

        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_compliant)
        stats_layout.addWidget(self.stat_non_compliant)
        stats_layout.addWidget(self.stat_included)

        main_layout.addLayout(stats_layout)

        # --- 2. Action Bar & Search ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search voter name...")
        self.search_input.textChanged.connect(self._filter_table)
        action_layout.addWidget(self.search_input, stretch=2)

        btn_select_all = PixelButton("Select All", variant="parchment", parent=self)
        btn_select_all.clicked.connect(self._select_all)
        action_layout.addWidget(btn_select_all)

        btn_deselect_all = PixelButton("Deselect All", variant="parchment", parent=self)
        btn_deselect_all.clicked.connect(self._deselect_all)
        action_layout.addWidget(btn_deselect_all)

        btn_exclude_invalid = PixelButton("Exclude Non-Compliant", variant="red", parent=self)
        btn_exclude_invalid.setToolTip("Quickly unchecks all ballots that have compliance issues (<5 ranked, skipped numbers, etc.)")
        btn_exclude_invalid.clicked.connect(self._exclude_non_compliant)
        action_layout.addWidget(btn_exclude_invalid)

        btn_reset = PixelButton("Reset Defaults", variant="parchment", parent=self)
        btn_reset.clicked.connect(self._reset_defaults)
        action_layout.addWidget(btn_reset)

        main_layout.addLayout(action_layout)

        # --- 3. Submissions Table ---
        table_card = RetroCard(title="SUBMISSIONS LIST", parent=self)
        table_layout = QVBoxLayout()
        table_layout.setSpacing(6)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Include", "Voter Name", "Ranked Count", "Compliance Status", "Actions"])
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)

        table_layout.addWidget(self.table)
        table_card.set_content_layout(table_layout)
        main_layout.addWidget(table_card, stretch=1)

        # --- 4. Bottom Action Banner ---
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(4, 4, 4, 4)
        bottom_bar.setSpacing(12)

        chicken_sprite = AnimatedSpriteWidget.create_chicken(pecking=True, scale=2, parent=self)
        bottom_bar.addWidget(chicken_sprite)

        self.lbl_summary = QLabel("Load a CSV or ZIP file to begin analysis.")
        self.lbl_summary.setFont(ThemeManager.instance().get_font(12, bold=True))
        self.lbl_summary.setStyleSheet(f"color: {Colors.TEXT_DARK.name()};")
        bottom_bar.addWidget(self.lbl_summary, stretch=1)

        self.btn_calculate = PixelButton("Run Analysis", variant="green", font_size=13, parent=self)
        self.btn_calculate.setFixedHeight(40)
        self.btn_calculate.clicked.connect(self.calculation_requested.emit)
        bottom_bar.addWidget(self.btn_calculate)

        main_layout.addLayout(bottom_bar)

    def load_dataset(self, dataset: BallotDataset):
        self.dataset = dataset
        self.populate_table()
        self.update_stats()

    def update_stats(self):
        if not self.dataset:
            return
        total = self.dataset.total_ballots
        compliant = self.dataset.compliant_ballots_count
        non_compliant = self.dataset.non_compliant_ballots_count
        included = len(self.dataset.included_ballots)

        self.stat_total.update_value(str(total))
        self.stat_compliant.update_value(str(compliant))
        self.stat_non_compliant.update_value(str(non_compliant))
        self.stat_included.update_value(str(included), f"{included}/{total} ballots active")

        self.lbl_summary.setText(f"Ready: {included} of {total} ballots selected for Condorcet analysis.")
        self.btn_calculate.setEnabled(included > 0)

    def populate_table(self):
        if not self.dataset:
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(self.dataset.ballots))
        self._row_to_ballot.clear()

        for row_idx, ballot in enumerate(self.dataset.ballots):
            self._row_to_ballot[row_idx] = ballot

            # Col 0: Checkbox
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(6, 2, 6, 2)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk = QCheckBox()
            chk.setChecked(ballot.included)
            chk.toggled.connect(lambda state, b=ballot: self._on_ballot_toggled(b, state))
            chk_layout.addWidget(chk)
            self.table.setCellWidget(row_idx, 0, chk_widget)

            # Col 1: Voter Name
            name_item = QTableWidgetItem(ballot.voter_name)
            name_item.setFont(ThemeManager.instance().get_font(11, bold=True))
            name_item.setToolTip("Double-click to inspect voter's full ballot")
            self.table.setItem(row_idx, 1, name_item)

            # Col 2: Ranked Count
            count_text = f"{ballot.num_ranked} / {len(ballot.all_candidates)}"
            count_item = QTableWidgetItem(count_text)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            count_item.setFont(ThemeManager.instance().get_font(11))
            self.table.setItem(row_idx, 2, count_item)

            # Col 3: Compliance Badge
            badge_widget = ComplianceBadge(ballot.is_compliant, ballot.issues, parent=self)
            self.table.setCellWidget(row_idx, 3, badge_widget)

            # Col 4: Action Button
            btn_view = PixelButton("View Ballot", variant="parchment", font_size=10, parent=self)
            btn_view.setFixedHeight(26)
            btn_view.clicked.connect(lambda _, b=ballot: self.open_ballot_dialog(b))
            
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.addWidget(btn_view)
            self.table.setCellWidget(row_idx, 4, btn_container)

            self.table.setRowHeight(row_idx, 34)

    def _on_ballot_toggled(self, ballot: Ballot, state: bool):
        ballot.included = state
        self.update_stats()
        self.ballot_selection_changed.emit()

    def _on_row_double_clicked(self, row: int, col: int):
        ballot = self._row_to_ballot.get(row)
        if ballot:
            self.open_ballot_dialog(ballot)

    def open_ballot_dialog(self, ballot: Ballot):
        dialog = BallotDetailDialog(ballot, parent=self)
        dialog.inclusion_toggled.connect(lambda _: self._refresh_checkboxes_and_stats())
        dialog.exec()
        self._refresh_checkboxes_and_stats()

    def _refresh_checkboxes_and_stats(self):
        self.populate_table()
        self.update_stats()
        self.ballot_selection_changed.emit()

    def _select_all(self):
        if not self.dataset:
            return
        self.dataset.set_all_included(True)
        self._refresh_checkboxes_and_stats()

    def _deselect_all(self):
        if not self.dataset:
            return
        self.dataset.set_all_included(False)
        self._refresh_checkboxes_and_stats()

    def _exclude_non_compliant(self):
        if not self.dataset:
            return
        self.dataset.exclude_non_compliant()
        self._refresh_checkboxes_and_stats()

    def _reset_defaults(self):
        if not self.dataset:
            return
        self.dataset.reset_defaults()
        self._refresh_checkboxes_and_stats()

    def _filter_table(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            name_text = name_item.text().lower() if name_item else ""
            self.table.setRowHidden(row, query not in name_text)
