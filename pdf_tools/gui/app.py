"""
Main GUI application entry point
"""

import sys

import flet as ft

from .main_window import MainWindow


class PDFToolsGUI:
    """Main GUI application class"""

    def __init__(self):
        self.app = None
        self.main_window = None

    def run(self):
        """Run the GUI application"""
        ft.app(target=self._main, name="pdf-tools", assets_dir=None)

    def _main(self, page: ft.Page):
        """Main function for Flet app"""
        page.title = "PDF Tools"
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.scroll = ft.ScrollMode.AUTO
        page.window.width = 800
        page.window.height = 600
        page.window.min_width = 600
        page.window.min_height = 500

        self.main_window = MainWindow(page)
        page.add(self.main_window)


def main():
    """Entry point for GUI application"""
    gui = PDFToolsGUI()
    gui.run()


if __name__ == "__main__":
    main()
