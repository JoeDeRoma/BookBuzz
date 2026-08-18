import os
import glob
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QFileDialog, QMessageBox, QStatusBar
)

from engine.ballot_parser import parse_ballot_dataset, BallotDataset
from engine.ranked_pairs import solve_ranked_pairs, RankedPairsResult
from ui.theme import ThemeManager, Colors, get_asset_path
from ui.widgets.pixel_button import PixelButton
from ui.widgets.animated_sprite import AnimatedSpriteWidget
from ui.widgets.retro_frame import RetroFrame
from ui.tabs.submissions_tab import SubmissionsTab
from ui.tabs.standings_tab import StandingsTab
from ui.tabs.matrix_tab import MatrixTab


class MainWindow(QMainWindow):
    """
    Main application window for Book Buzz — Voting Resolver.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Buzz — Voting Resolver")
        self.resize(1000, 750)
        self.setMinimumSize(850, 600)
        self.setAcceptDrops(True)

        self.current_file_path: Optional[str] = None
        self.dataset: Optional[BallotDataset] = None
        self.current_result: Optional[RankedPairsResult] = None

        self._init_ui()
        self._auto_load_default_file()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 10, 14, 10)
        root_layout.setSpacing(10)

        # --- 1. Header Banner ---
        header_frame = RetroFrame(
            central_widget,
            content_margins=(16, 8, 16, 8)
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(12)

        # Left Chicken Mascot
        chicken_mascot = AnimatedSpriteWidget.create_chicken(pecking=False, scale=2, parent=header_frame)
        header_layout.addWidget(chicken_mascot)

        # Title text
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_app_title = QLabel("BOOK BUZZ")
        lbl_app_title.setFont(ThemeManager.instance().get_font(18, bold=True))
        lbl_app_title.setStyleSheet(f"color: {Colors.TEXT_DARK.name()}; letter-spacing: 1px;")
        title_box.addWidget(lbl_app_title)

        lbl_app_sub = QLabel("Ranked Pairs (Tideman Condorcet) Ballot Compliance & Voting Resolver")
        lbl_app_sub.setFont(ThemeManager.instance().get_font(10))
        lbl_app_sub.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()};")
        title_box.addWidget(lbl_app_sub)
        header_layout.addLayout(title_box, stretch=1)

        # Right Cow Mascot
        cow_mascot = AnimatedSpriteWidget.create_cow(scale=2, parent=header_frame)
        header_layout.addWidget(cow_mascot)

        root_layout.addWidget(header_frame)

        # --- 2. Top File Bar ---
        file_bar = QHBoxLayout()
        file_bar.setSpacing(8)

        btn_browse = PixelButton("Open CSV or ZIP", variant="gold", font_size=11, parent=self)
        btn_browse.clicked.connect(self._browse_file)
        file_bar.addWidget(btn_browse)

        self.btn_reload = PixelButton("Reload", variant="parchment", font_size=11, parent=self)
        self.btn_reload.clicked.connect(self._reload_file)
        self.btn_reload.setEnabled(False)
        file_bar.addWidget(self.btn_reload)

        self.lbl_file_status = QLabel("No file loaded. Drag & drop a .csv or .zip file here, or click 'Open CSV or ZIP'.")
        self.lbl_file_status.setFont(ThemeManager.instance().get_font(10))
        self.lbl_file_status.setStyleSheet(
            f"color: {Colors.TEXT_MUTED.name()}; background-color: {Colors.BG_CARD.name()}; "
            f"border: 2px dashed {Colors.BORDER_LIGHT.name()}; padding: 6px 12px; border-radius: 4px;"
        )
        file_bar.addWidget(self.lbl_file_status, stretch=1)

        root_layout.addLayout(file_bar)

        # --- 3. Main Tabs ---
        self.tabs = QTabWidget(self)

        self.tab_submissions = SubmissionsTab(self)
        self.tab_submissions.calculation_requested.connect(self.run_analysis)
        self.tab_submissions.ballot_selection_changed.connect(self._on_ballots_changed)

        self.tab_standings = StandingsTab(self)
        self.tab_matrix = MatrixTab(self)

        self.tabs.addTab(self.tab_submissions, "1. Submissions & Compliance")
        self.tabs.addTab(self.tab_standings, "2. Winner & Full Standings")
        self.tabs.addTab(self.tab_matrix, "3. Pairwise Matchups")

        root_layout.addWidget(self.tabs, stretch=1)

        # --- Status Bar ---
        self.status_bar = QStatusBar(self)
        self.status_bar.setStyleSheet(f"color: {Colors.TEXT_MUTED.name()}; background-color: {Colors.BG_PARCHMENT.name()}; border-top: 1px solid {Colors.BORDER_LIGHT.name()};")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

    def _auto_load_default_file(self):
        """Auto-detects and loads any Book Choice CSV or ZIP in the working directory."""
        candidates = glob.glob("Book Choice - *.csv") + glob.glob("Book Choice - *.zip")
        if candidates:
            candidates.sort(reverse=True)
            self.load_file(candidates[0])

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Voting Ballots File",
            "",
            "Supported Files (*.csv *.zip);;CSV Files (*.csv);;ZIP Archives (*.zip);;All Files (*)"
        )
        if file_path:
            self.load_file(file_path)

    def _reload_file(self):
        if self.current_file_path and os.path.exists(self.current_file_path):
            self.load_file(self.current_file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(u.toLocalFile().lower().endswith(('.csv', '.zip')) for u in urls):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for u in urls:
            local_path = u.toLocalFile()
            if local_path.lower().endswith(('.csv', '.zip')):
                self.load_file(local_path)
                break

    def load_file(self, file_path: str):
        try:
            dataset = parse_ballot_dataset(file_path)
            self.current_file_path = file_path
            self.dataset = dataset
            self.btn_reload.setEnabled(True)

            self.lbl_file_status.setText(f"Loaded: {dataset.source_name} ({dataset.total_ballots} ballots, {len(dataset.candidates)} candidates)")
            self.lbl_file_status.setStyleSheet(
                f"color: {Colors.TEXT_DARK.name()}; background-color: {Colors.BG_CARD.name()}; "
                f"border: 2px solid {Colors.BORDER_DARK.name()}; padding: 6px 12px; border-radius: 4px;"
            )

            self.tab_submissions.load_dataset(dataset)
            self.status_bar.showMessage(f"Loaded '{dataset.source_name}' with {dataset.total_ballots} ballots.")

            # Automatically run initial analysis
            self.run_analysis(switch_tab=False)

        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"Failed to parse file '{os.path.basename(file_path)}':\n\n{str(e)}")
            self.status_bar.showMessage("Error loading file.")

    def _on_ballots_changed(self):
        # Update results automatically when checkboxes change
        if self.dataset:
            self.run_analysis(switch_tab=False)

    def run_analysis(self, switch_tab: bool = True):
        if not self.dataset:
            QMessageBox.warning(self, "No Data", "Please load a CSV or ZIP file first.")
            return

        try:
            result = solve_ranked_pairs(self.dataset.candidates, self.dataset.ballots)
            self.current_result = result

            self.tab_standings.display_results(result)
            self.tab_matrix.display_results(result)

            self.status_bar.showMessage(f"Analysis complete. Winner: {result.winner_name} (RP Score: {result.standings[0].score if result.standings else 0})")

            if switch_tab:
                self.tabs.setCurrentIndex(1)  # Switch to Winner & Standings tab

        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Failed to run Ranked Pairs analysis:\n\n{str(e)}")
