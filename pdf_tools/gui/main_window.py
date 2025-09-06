"""
Main window for PDF Tools GUI application using Flet
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

import flet as ft

from ..common.pdf_tools import PDFTools

logger = logging.getLogger(__name__)


class MainWindow(ft.Column):
    """Main application window using Flet"""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.pdf_tools = PDFTools()
        self.expand = True
        self.spacing = 10
        
        # Create file picker
        self.file_picker = ft.FilePicker(
            on_result=self._on_file_picker_result
        )
        self.page.overlay.append(self.file_picker)
        
        # Store the current operation for file picker
        self._current_file_operation = None
        
        # Create UI components
        self._create_ui()

    def _create_ui(self):
        """Initialize the user interface"""
        # Title
        title = ft.Text(
            "PDF Tools",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Create tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
            tabs=[
                self._create_merge_tab(),
                self._create_compress_tab(),
                self._create_convert_tab(),
            ],
        )

        # Add components to column
        self.controls = [
            ft.Container(content=title, alignment=ft.alignment.center, padding=10),
            self.tabs,
        ]

    def _create_merge_tab(self) -> ft.Tab:
        """Create the PDF merge tab"""
        # File list
        self.merge_file_list = ft.ListView(
            expand=True,
            spacing=5,
            height=200,
        )

        # Output file input
        self.merge_output = ft.TextField(
            label="Output file",
            value="merged_output.pdf",
            expand=True,
        )

        # Progress bar
        self.merge_progress = ft.ProgressBar(visible=False)

        # Status text
        self.merge_status = ft.Text("Ready")

        # Buttons
        add_files_btn = ft.ElevatedButton(
            "Add PDF Files",
            icon=ft.Icons.ADD,
            on_click=self._add_merge_files,
        )

        remove_file_btn = ft.ElevatedButton(
            "Remove Selected",
            icon=ft.Icons.REMOVE,
            on_click=self._remove_merge_file,
        )

        clear_files_btn = ft.ElevatedButton(
            "Clear All",
            icon=ft.Icons.CLEAR,
            on_click=self._clear_merge_files,
        )

        browse_output_btn = ft.ElevatedButton(
            "Browse...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._browse_merge_output,
        )

        self.merge_btn = ft.ElevatedButton(
            "Merge PDFs",
            icon=ft.Icons.MERGE,
            on_click=self._merge_pdfs,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
        )

        # Layout
        content = ft.Column([
            ft.Text("Select PDF Files", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.merge_file_list,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=5,
            ),
            ft.Row([
                add_files_btn,
                remove_file_btn,
                clear_files_btn,
            ], spacing=10),
            ft.Divider(),
            ft.Text("Output Settings", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.merge_output,
                browse_output_btn,
            ], spacing=10),
            ft.Divider(),
            self.merge_progress,
            self.merge_status,
            self.merge_btn,
        ], spacing=10, expand=True)

        return ft.Tab(
            text="Merge PDFs",
            icon=ft.Icons.MERGE_TYPE,
            content=ft.Container(content=content, padding=20),
        )

    def _create_compress_tab(self) -> ft.Tab:
        """Create the PDF compress tab"""
        # Input file
        self.compress_input = ft.TextField(
            label="Input PDF file",
            expand=True,
        )

        # Quality dropdown
        self.compress_quality = ft.Dropdown(
            label="Quality",
            value="printer",
            options=[
                ft.dropdown.Option("printer", "Printer"),
                ft.dropdown.Option("ebook", "E-book"),
                ft.dropdown.Option("screen", "Screen"),
                ft.dropdown.Option("prepress", "Prepress"),
            ],
        )

        # Output file
        self.compress_output = ft.TextField(
            label="Output file",
            expand=True,
        )

        # Progress bar
        self.compress_progress = ft.ProgressBar(visible=False)

        # Status text
        self.compress_status = ft.Text("Ready")

        # Buttons
        browse_input_btn = ft.ElevatedButton(
            "Browse...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._browse_compress_input,
        )

        browse_output_btn = ft.ElevatedButton(
            "Browse...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._browse_compress_output,
        )

        self.compress_btn = ft.ElevatedButton(
            "Compress PDF",
            icon=ft.Icons.COMPRESS,
            on_click=self._compress_pdf,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
            ),
        )

        # Layout
        content = ft.Column([
            ft.Text("Input PDF File", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.compress_input,
                browse_input_btn,
            ], spacing=10),
            ft.Divider(),
            ft.Text("Compression Settings", size=16, weight=ft.FontWeight.BOLD),
            self.compress_quality,
            ft.Row([
                self.compress_output,
                browse_output_btn,
            ], spacing=10),
            ft.Divider(),
            self.compress_progress,
            self.compress_status,
            self.compress_btn,
        ], spacing=10, expand=True)

        return ft.Tab(
            text="Compress PDF",
            icon=ft.Icons.COMPRESS,
            content=ft.Container(content=content, padding=20),
        )

    def _create_convert_tab(self) -> ft.Tab:
        """Create the convert tab"""
        # File list
        self.convert_file_list = ft.ListView(
            expand=True,
            spacing=5,
            height=200,
        )

        # Conversion settings
        self.convert_from = ft.Dropdown(
            label="From",
            value="pdf",
            options=[
                ft.dropdown.Option("pdf", "PDF"),
                ft.dropdown.Option("image", "Image"),
            ],
            on_change=self._on_convert_from_change,
        )

        self.convert_to = ft.Dropdown(
            label="To",
            value="image",
            options=[
                ft.dropdown.Option("pdf", "PDF"),
                ft.dropdown.Option("image", "Image"),
            ],
        )

        self.convert_format = ft.Dropdown(
            label="Image Format",
            value="png",
            options=[
                ft.dropdown.Option("png", "PNG"),
                ft.dropdown.Option("jpg", "JPG"),
                ft.dropdown.Option("jpeg", "JPEG"),
                ft.dropdown.Option("bmp", "BMP"),
                ft.dropdown.Option("tiff", "TIFF"),
                ft.dropdown.Option("webp", "WebP"),
            ],
        )

        self.convert_dpi = ft.TextField(
            label="DPI",
            value="200",
            width=100,
            input_filter=ft.NumbersOnlyInputFilter(),
        )

        # Output file
        self.convert_output = ft.TextField(
            label="Output base name",
            value="converted_output",
            expand=True,
        )

        # Progress bar
        self.convert_progress = ft.ProgressBar(visible=False)

        # Status text
        self.convert_status = ft.Text("Ready")

        # Buttons
        add_convert_files_btn = ft.ElevatedButton(
            "Add Files",
            icon=ft.Icons.ADD,
            on_click=self._add_convert_files,
        )

        remove_convert_file_btn = ft.ElevatedButton(
            "Remove Selected",
            icon=ft.Icons.REMOVE,
            on_click=self._remove_convert_file,
        )

        clear_convert_files_btn = ft.ElevatedButton(
            "Clear All",
            icon=ft.Icons.CLEAR,
            on_click=self._clear_convert_files,
        )

        browse_convert_output_btn = ft.ElevatedButton(
            "Browse...",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._browse_convert_output,
        )

        self.convert_btn = ft.ElevatedButton(
            "Convert Files",
            icon=ft.Icons.TRANSFORM,
            on_click=self._convert_files,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE,
            ),
        )

        # Layout
        content = ft.Column([
            ft.Text("Select Files", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=self.convert_file_list,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=5,
            ),
            ft.Row([
                add_convert_files_btn,
                remove_convert_file_btn,
                clear_convert_files_btn,
            ], spacing=10),
            ft.Divider(),
            ft.Text("Conversion Settings", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.convert_from,
                self.convert_to,
            ], spacing=10),
            ft.Row([
                self.convert_format,
                self.convert_dpi,
            ], spacing=10),
            ft.Row([
                self.convert_output,
                browse_convert_output_btn,
            ], spacing=10),
            ft.Divider(),
            self.convert_progress,
            self.convert_status,
            self.convert_btn,
        ], spacing=10, expand=True)

        return ft.Tab(
            text="Convert",
            icon=ft.Icons.TRANSFORM,
            content=ft.Container(content=content, padding=20),
        )

    # File picker callback
    def _on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if not e.files:
            return
            
        if self._current_file_operation == "add_merge_files":
            for file in e.files:
                file_item = ft.ListTile(
                    leading=ft.Icon(ft.Icons.PICTURE_AS_PDF),
                    title=ft.Text(file.name),
                    subtitle=ft.Text(file.path),
                    data=file.path,
                )
                self.merge_file_list.controls.append(file_item)
        elif self._current_file_operation == "merge_output":
            self.merge_output.value = e.path
        elif self._current_file_operation == "compress_input":
            file_path = e.files[0].path
            self.compress_input.value = file_path
            # Auto-set output filename
            path = Path(file_path)
            output_name = f"{path.stem}_compressed{path.suffix}"
            self.compress_output.value = str(path.parent / output_name)
        elif self._current_file_operation == "compress_output":
            self.compress_output.value = e.path
        elif self._current_file_operation == "add_convert_files":
            for file in e.files:
                from_format = self.convert_from.value
                icon = ft.Icons.PICTURE_AS_PDF if from_format == "pdf" else ft.Icons.IMAGE
                file_item = ft.ListTile(
                    leading=ft.Icon(icon),
                    title=ft.Text(file.name),
                    subtitle=ft.Text(file.path),
                    data=file.path,
                )
                self.convert_file_list.controls.append(file_item)
        elif self._current_file_operation == "convert_output":
            # Remove extension to get base name
            base_name = Path(e.path).stem
            self.convert_output.value = base_name
            
        self._current_file_operation = None
        self.page.update()

    # Event handlers for merge tab
    def _add_merge_files(self, e):
        """Add PDF files for merging"""
        self._current_file_operation = "add_merge_files"
        self.file_picker.pick_files(
            dialog_title="Select PDF Files",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=True,
        )

    def _remove_merge_file(self, e):
        """Remove selected file from merge list"""
        # For simplicity, remove the last item
        if self.merge_file_list.controls:
            self.merge_file_list.controls.pop()
            self.page.update()

    def _clear_merge_files(self, e):
        """Clear all files from merge list"""
        self.merge_file_list.controls.clear()
        self.page.update()

    def _browse_merge_output(self, e):
        """Browse for merge output file"""
        self._current_file_operation = "merge_output"
        self.file_picker.save_file(
            dialog_title="Save Merged PDF",
            file_name="merged_output.pdf",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
        )

    def _merge_pdfs(self, e):
        """Start PDF merge operation"""
        if not self.merge_file_list.controls:
            self._show_error("Please select PDF files to merge.")
            return

        if not self.merge_output.value:
            self._show_error("Please specify output file.")
            return

        # Get file list
        files = [item.data for item in self.merge_file_list.controls]
        output_file = self.merge_output.value

        self._run_operation(
            "merge",
            files,
            output_file,
            progress_bar=self.merge_progress,
            status_text=self.merge_status,
            button=self.merge_btn,
        )

    # Event handlers for compress tab
    def _browse_compress_input(self, e):
        """Browse for compress input file"""
        self._current_file_operation = "compress_input"
        self.file_picker.pick_files(
            dialog_title="Select PDF File",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=False,
        )

    def _browse_compress_output(self, e):
        """Browse for compress output file"""
        self._current_file_operation = "compress_output"
        self.file_picker.save_file(
            dialog_title="Save Compressed PDF",
            file_name="compressed.pdf",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
        )

    def _compress_pdf(self, e):
        """Start PDF compression operation"""
        input_file = self.compress_input.value
        output_file = self.compress_output.value
        quality = self.compress_quality.value

        if not input_file:
            self._show_error("Please select input PDF file.")
            return

        if not output_file:
            self._show_error("Please specify output file.")
            return

        self._run_operation(
            "compress",
            input_file,
            output_file,
            quality,
            progress_bar=self.compress_progress,
            status_text=self.compress_status,
            button=self.compress_btn,
        )

    # Event handlers for convert tab
    def _on_convert_from_change(self, e):
        """Handle conversion from format change"""
        # Update file picker filter based on selection
        self.page.update()

    def _add_convert_files(self, e):
        """Add files for conversion"""
        self._current_file_operation = "add_convert_files"
        from_format = self.convert_from.value
        
        if from_format == "pdf":
            self.file_picker.pick_files(
                dialog_title="Select PDF Files",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
                allow_multiple=True,
            )
        else:
            self.file_picker.pick_files(
                dialog_title="Select Image Files",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
                allow_multiple=True,
            )

    def _remove_convert_file(self, e):
        """Remove selected file from convert list"""
        if self.convert_file_list.controls:
            self.convert_file_list.controls.pop()
            self.page.update()

    def _clear_convert_files(self, e):
        """Clear all files from convert list"""
        self.convert_file_list.controls.clear()
        self.page.update()

    def _browse_convert_output(self, e):
        """Browse for convert output location"""
        self._current_file_operation = "convert_output"
        to_format = self.convert_to.value
        
        if to_format == "pdf":
            self.file_picker.save_file(
                dialog_title="Save PDF",
                file_name="converted_output.pdf",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )
        else:
            output_format = self.convert_format.value
            self.file_picker.save_file(
                dialog_title=f"Save {output_format.upper()}",
                file_name=f"converted_output.{output_format}",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[output_format],
            )

    def _convert_files(self, e):
        """Convert files"""
        files = [item.data for item in self.convert_file_list.controls]

        if not files:
            self._show_error("Please select files to convert.")
            return

        from_format = self.convert_from.value
        to_format = self.convert_to.value
        output_format = self.convert_format.value
        output_base = self.convert_output.value
        dpi = int(self.convert_dpi.value) if self.convert_dpi.value.isdigit() else 200

        if not output_base:
            self._show_error("Please specify output base name.")
            return

        # Generate output filename
        if to_format == "pdf":
            output_file = f"{output_base}.pdf"
        else:
            output_file = f"{output_base}.{output_format}"

        self._run_operation(
            "convert",
            files,
            from_format,
            to_format,
            output_format,
            output_file,
            dpi,
            [],  # rotate_list (not implemented in GUI yet)
            progress_bar=self.convert_progress,
            status_text=self.convert_status,
            button=self.convert_btn,
        )

    # Utility methods
    def _run_operation(self, operation, *args, progress_bar=None, status_text=None, button=None, **kwargs):
        """Run a background operation"""
        import threading
        
        def run_operation_thread():
            original_text = button.text if button else None
            
            try:
                # Setup UI for operation
                if progress_bar:
                    progress_bar.visible = True
                    
                if button:
                    button.disabled = True
                    button.text = "Processing..."
                    
                if status_text:
                    status_text.value = f"Running {operation} operation..."
                    
                self.page.update()

                # Run operation
                if operation == "merge":
                    self.pdf_tools.merge_pdf(*args, **kwargs)
                elif operation == "compress":
                    self.pdf_tools.compress_pdf(*args, **kwargs)
                elif operation == "convert":
                    self._run_convert(*args, **kwargs)

                # Success
                if status_text:
                    status_text.value = "Operation completed successfully!"
                self._show_success("Operation completed successfully!")

            except Exception as ex:
                logger.error(f"Operation failed: {ex}")
                if status_text:
                    status_text.value = "Ready"
                self._show_error(f"Operation failed: {ex}")

            finally:
                # Restore UI
                if progress_bar:
                    progress_bar.visible = False
                    
                if button:
                    button.disabled = False
                    if original_text:
                        button.text = original_text
                    
                self.page.update()
        
        # Run in background thread
        threading.Thread(target=run_operation_thread, daemon=True).start()

    def _run_convert(self, files, from_format, to_format, output_format, output, dpi, rotate_list):
        """Run convert operation"""
        if from_format == "image" and to_format == "pdf":
            self.pdf_tools.image_to_pdf(files, rotate_list, output)
        elif from_format == "pdf" and to_format == "image":
            self.pdf_tools.pdf_to_image(files, output, dpi, output_format)

    def _show_error(self, message: str):
        """Show error message"""
        self.page.open(
            ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.close(e.control.parent))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    def _show_success(self, message: str):
        """Show success message"""
        self.page.open(
            ft.AlertDialog(
                title=ft.Text("Success"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.close(e.control.parent))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )