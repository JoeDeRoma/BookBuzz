import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ui.theme import ThemeManager, get_app_stylesheet, get_asset_path
from ui.main_window import MainWindow


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("BookBuzz")
    app.setOrganizationName("BookBuzz")

    # Initialize theme and custom pixel font
    theme = ThemeManager.instance()
    app.setFont(theme.get_font(12))
    app.setStyleSheet(get_app_stylesheet())

    # Set Application Icon
    ico_path = get_asset_path().parent / "bookclub.ico"
    if ico_path.exists():
        app.setWindowIcon(QIcon(str(ico_path)))

    # Check for headless test mode
    if "--test" in sys.argv:
        print("Test mode flag detected: creating window instance and verifying execution...")
        window = MainWindow()
        print("Window initialized successfully.")
        if window.dataset:
            print(f"Default dataset auto-loaded: {window.dataset.source_name} ({window.dataset.total_ballots} ballots)")
            window.run_analysis(switch_tab=False)
            if window.current_result:
                print(f"Analysis calculated successfully. Winner: {window.current_result.winner_name}")
        print("Self-test completed without errors.")
        return 0

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
