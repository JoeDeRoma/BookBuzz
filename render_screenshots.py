import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

from ui.theme import ThemeManager, get_app_stylesheet
from ui.main_window import MainWindow
from ui.dialogs.ballot_detail_dialog import BallotDetailDialog


def capture_all_views():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(ThemeManager.instance().get_font(12))
    app.setStyleSheet(get_app_stylesheet())

    output_dir = Path("C:/Users/josep/.gemini/antigravity-ide/brain/62d4417a-98b4-4500-b332-332e6ff679e1")
    output_dir.mkdir(parents=True, exist_ok=True)

    window = MainWindow()
    window.resize(1020, 760)
    window.show()

    app.processEvents()

    # 1. Submissions Tab Screenshot
    window.tabs.setCurrentIndex(0)
    app.processEvents()
    pixmap_sub = window.grab()
    pixmap_sub.save(str(output_dir / "view_submissions_tab.png"))
    print("Saved view_submissions_tab.png")

    # 2. Winner Standings Tab Screenshot
    window.run_analysis(switch_tab=True)
    window.tabs.setCurrentIndex(1)
    app.processEvents()
    pixmap_standings = window.grab()
    pixmap_standings.save(str(output_dir / "view_standings_tab.png"))
    print("Saved view_standings_tab.png")

    # 3. Pairwise Matrix Tab Screenshot
    window.tabs.setCurrentIndex(2)
    app.processEvents()
    pixmap_matrix = window.grab()
    pixmap_matrix.save(str(output_dir / "view_matrix_tab.png"))
    print("Saved view_matrix_tab.png")

    # 4. Ballot Detail Dialog Screenshot
    if window.dataset and window.dataset.ballots:
        # Find an invalid ballot and a valid ballot
        invalid_ballot = next((b for b in window.dataset.ballots if not b.is_compliant), window.dataset.ballots[0])
        dialog = BallotDetailDialog(invalid_ballot)
        dialog.resize(560, 620)
        dialog.show()
        app.processEvents()
        pixmap_dialog = dialog.grab()
        pixmap_dialog.save(str(output_dir / "view_ballot_detail.png"))
        print("Saved view_ballot_detail.png")
        dialog.close()

    window.close()
    print("All screenshots successfully captured!")


if __name__ == "__main__":
    capture_all_views()
