"""
Main GUI application entry point
"""

import sys

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


class PDFToolsGUI:
    """Main GUI application class"""

    def __init__(self):
        self.app = None
        self.main_window = None

    def run(self):
        """Run the GUI application"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("PDF Tools")
        self.app.setApplicationVersion("0.1.0")
        self.app.setOrganizationName("thsvkd")

        self.main_window = MainWindow()
        self.main_window.show()

        return self.app.exec()


def main():
    """Entry point for GUI application"""
    gui = PDFToolsGUI()
    sys.exit(gui.run())


if __name__ == "__main__":
    main()
