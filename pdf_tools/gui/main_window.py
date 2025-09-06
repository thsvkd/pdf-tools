"""
Main window for PDF Tools GUI application
"""

import logging
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..common.pdf_tools import PDFTools

logger = logging.getLogger(__name__)


class WorkerThread(QThread):
    """Worker thread for PDF processing operations"""

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.pdf_tools = PDFTools()

    def run(self):
        """Run the operation in background thread"""
        try:
            if self.operation == "merge":
                self.pdf_tools.merge_pdf(*self.args, **self.kwargs)
            elif self.operation == "compress":
                self.pdf_tools.compress_pdf(*self.args, **self.kwargs)
            elif self.operation == "convert":
                self._run_convert(*self.args, **self.kwargs)

            self.finished.emit("Operation completed successfully!")

        except Exception as e:
            logger.error(f"Operation failed: {e}")
            self.error.emit(str(e))

    def _run_convert(self, files, from_format, to_format, output_format, output, dpi, rotate_list):
        """Run convert operation"""
        if from_format == "image" and to_format == "pdf":
            self.pdf_tools.image_to_pdf(files, rotate_list, output)
        elif from_format == "pdf" and to_format == "image":
            self.pdf_tools.pdf_to_image(files, output, dpi, output_format)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.pdf_tools = PDFTools()
        self.worker_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("PDF Tools")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Add title label
        title_label = QLabel("PDF Tools")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_merge_tab()
        self.create_compress_tab()
        self.create_convert_tab()

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_merge_tab(self):
        """Create the PDF merge tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File selection group
        file_group = QGroupBox("Select PDF Files")
        file_layout = QVBoxLayout(file_group)

        self.merge_file_list = QListWidget()
        file_layout.addWidget(self.merge_file_list)

        button_layout = QHBoxLayout()
        add_files_btn = QPushButton("Add PDF Files")
        add_files_btn.clicked.connect(self.add_merge_files)
        remove_file_btn = QPushButton("Remove Selected")
        remove_file_btn.clicked.connect(self.remove_merge_file)
        clear_files_btn = QPushButton("Clear All")
        clear_files_btn.clicked.connect(self.clear_merge_files)

        button_layout.addWidget(add_files_btn)
        button_layout.addWidget(remove_file_btn)
        button_layout.addWidget(clear_files_btn)
        file_layout.addLayout(button_layout)

        layout.addWidget(file_group)

        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)

        self.merge_output_edit = QLineEdit("merged_output.pdf")
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_merge_output)

        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.merge_output_edit)
        output_path_layout.addWidget(output_browse_btn)

        output_layout.addRow("Output File:", output_path_layout)
        layout.addWidget(output_group)

        # Progress bar
        self.merge_progress = QProgressBar()
        self.merge_progress.setVisible(False)
        layout.addWidget(self.merge_progress)

        # Merge button
        self.merge_btn = QPushButton("Merge PDFs")
        self.merge_btn.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.merge_btn)

        self.tab_widget.addTab(tab, "Merge PDFs")

    def create_compress_tab(self):
        """Create the PDF compress tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Input file group
        input_group = QGroupBox("Input PDF File")
        input_layout = QFormLayout(input_group)

        self.compress_input_edit = QLineEdit()
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.clicked.connect(self.browse_compress_input)

        input_layout_h = QHBoxLayout()
        input_layout_h.addWidget(self.compress_input_edit)
        input_layout_h.addWidget(input_browse_btn)

        input_layout.addRow("PDF File:", input_layout_h)
        layout.addWidget(input_group)

        # Settings group
        settings_group = QGroupBox("Compression Settings")
        settings_layout = QFormLayout(settings_group)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["printer", "ebook", "screen", "prepress"])
        self.quality_combo.setCurrentText("printer")
        settings_layout.addRow("Quality:", self.quality_combo)

        self.compress_output_edit = QLineEdit()
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_compress_output)

        output_layout_h = QHBoxLayout()
        output_layout_h.addWidget(self.compress_output_edit)
        output_layout_h.addWidget(output_browse_btn)

        settings_layout.addRow("Output File:", output_layout_h)
        layout.addWidget(settings_group)

        # Progress bar
        self.compress_progress = QProgressBar()
        self.compress_progress.setVisible(False)
        layout.addWidget(self.compress_progress)

        # Compress button
        self.compress_btn = QPushButton("Compress PDF")
        self.compress_btn.clicked.connect(self.compress_pdf)
        layout.addWidget(self.compress_btn)

        self.tab_widget.addTab(tab, "Compress PDF")

    # File selection methods
    def add_merge_files(self):
        """Add PDF files for merging"""
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        for file in files:
            self.merge_file_list.addItem(file)

    def remove_merge_file(self):
        """Remove selected file from merge list"""
        current_row = self.merge_file_list.currentRow()
        if current_row >= 0:
            self.merge_file_list.takeItem(current_row)

    def clear_merge_files(self):
        """Clear all files from merge list"""
        self.merge_file_list.clear()

    def browse_merge_output(self):
        """Browse for merge output file"""
        file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if file:
            self.merge_output_edit.setText(file)

    def browse_compress_input(self):
        """Browse for compress input file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.compress_input_edit.setText(file)
            # Auto-set output filename
            path = Path(file)
            output_name = f"{path.stem}_compressed{path.suffix}"
            self.compress_output_edit.setText(str(path.parent / output_name))

    def browse_compress_output(self):
        """Browse for compress output file"""
        file, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "", "PDF Files (*.pdf)")
        if file:
            self.compress_output_edit.setText(file)

    # Processing methods
    def merge_pdfs(self):
        """Start PDF merge operation"""
        if self.merge_file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please select PDF files to merge.")
            return

        if not self.merge_output_edit.text():
            QMessageBox.warning(self, "Warning", "Please specify output file.")
            return

        # Get file list
        files = []
        for i in range(self.merge_file_list.count()):
            files.append(self.merge_file_list.item(i).text())

        output_file = self.merge_output_edit.text()

        self.start_operation(
            "merge",
            files,
            output_file,
            progress_bar=self.merge_progress,
            button=self.merge_btn,
        )

    def compress_pdf(self):
        """Start PDF compression operation"""
        input_file = self.compress_input_edit.text()
        output_file = self.compress_output_edit.text()
        quality = self.quality_combo.currentText()

        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select input PDF file.")
            return

        if not output_file:
            QMessageBox.warning(self, "Warning", "Please specify output file.")
            return

        self.start_operation(
            "compress",
            input_file,
            output_file,
            quality,
            progress_bar=self.compress_progress,
            button=self.compress_btn,
        )

    def start_operation(self, operation, *args, progress_bar=None, button=None, **kwargs):
        """Start a background operation"""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.information(self, "Info", "Another operation is already running.")
            return

        # Setup UI for operation
        if progress_bar:
            progress_bar.setVisible(True)
            progress_bar.setRange(0, 0)  # Indeterminate progress

        if button:
            button.setEnabled(False)
            button.setText("Processing...")

        self.statusBar().showMessage(f"Running {operation} operation...")

        # Start worker thread
        self.worker_thread = WorkerThread(operation, *args, **kwargs)
        self.worker_thread.finished.connect(lambda msg: self.on_operation_finished(msg, progress_bar, button))
        self.worker_thread.error.connect(lambda err: self.on_operation_error(err, progress_bar, button))
        self.worker_thread.start()

    def on_operation_finished(self, message, progress_bar=None, button=None):
        """Handle operation completion"""
        if progress_bar:
            progress_bar.setVisible(False)

        if button:
            button.setEnabled(True)
            self.reset_button_text(button)

        self.statusBar().showMessage("Ready")
        QMessageBox.information(self, "Success", message)

    def on_operation_error(self, error, progress_bar=None, button=None):
        """Handle operation error"""
        if progress_bar:
            progress_bar.setVisible(False)

        if button:
            button.setEnabled(True)
            self.reset_button_text(button)

        self.statusBar().showMessage("Ready")
        QMessageBox.critical(self, "Error", f"Operation failed: {error}")

    def reset_button_text(self, button):
        """Reset button text to original"""
        if button == self.merge_btn:
            button.setText("Merge PDFs")
        elif button == self.compress_btn:
            button.setText("Compress PDF")
        elif button == self.convert_btn:
            button.setText("Convert Files")

    # Convert tab methods
    def add_convert_files(self):
        """Add files for conversion"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        from_format = self.convert_from_combo.currentText()
        if from_format == "pdf":
            file_dialog.setNameFilter("PDF files (*.pdf)")
        else:
            file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)")

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file in files:
                self.convert_file_list.addItem(file)

    def remove_convert_file(self):
        """Remove selected file from convert list"""
        current_row = self.convert_file_list.currentRow()
        if current_row >= 0:
            self.convert_file_list.takeItem(current_row)

    def clear_convert_files(self):
        """Clear all files from convert list"""
        self.convert_file_list.clear()

    def browse_convert_output(self):
        """Browse for convert output location"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        to_format = self.convert_to_combo.currentText()
        if to_format == "pdf":
            file_dialog.setNameFilter("PDF files (*.pdf)")
            default_name = "converted_output.pdf"
        else:
            output_format = self.convert_output_format_combo.currentText()
            file_dialog.setNameFilter(f"{output_format.upper()} files (*.{output_format})")
            default_name = f"converted_output.{output_format}"

        file_dialog.selectFile(default_name)

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            # Remove extension to get base name
            base_name = Path(selected_file).stem
            self.convert_output_edit.setText(base_name)

    def convert_files(self):
        """Convert files"""
        files = []
        for i in range(self.convert_file_list.count()):
            files.append(self.convert_file_list.item(i).text())

        if not files:
            QMessageBox.warning(self, "No Files", "Please select files to convert.")
            return

        from_format = self.convert_from_combo.currentText()
        to_format = self.convert_to_combo.currentText()
        output_format = self.convert_output_format_combo.currentText()
        output_base = self.convert_output_edit.text()
        dpi = self.convert_dpi_spin.value()

        if not output_base:
            QMessageBox.warning(self, "No Output", "Please specify output base name.")
            return

        # Generate output filename
        if to_format == "pdf":
            output_file = f"{output_base}.pdf"
        else:
            output_file = f"{output_base}.{output_format}"

        # Start conversion
        self.convert_progress.setVisible(True)
        self.convert_btn.setText("Converting...")
        self.convert_btn.setEnabled(False)

        self.worker_thread = WorkerThread(
            "convert",
            files,
            from_format,
            to_format,
            output_format,
            output_file,
            dpi,
            [],  # rotate_list (not implemented in GUI yet)
        )
        self.worker_thread.progress.connect(self.convert_progress.setValue)
        self.worker_thread.finished.connect(
            lambda msg: self.on_operation_finished(msg, self.convert_progress, self.convert_btn)
        )
        self.worker_thread.error.connect(
            lambda err: self.on_operation_error(err, self.convert_progress, self.convert_btn)
        )
        self.worker_thread.start()

    def create_convert_tab(self):
        """Create the convert tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File selection group
        file_group = QGroupBox("Select Files")
        file_layout = QVBoxLayout(file_group)

        self.convert_file_list = QListWidget()
        file_layout.addWidget(self.convert_file_list)

        button_layout = QHBoxLayout()
        add_files_btn = QPushButton("Add Files")
        add_files_btn.clicked.connect(self.add_convert_files)
        remove_file_btn = QPushButton("Remove Selected")
        remove_file_btn.clicked.connect(self.remove_convert_file)
        clear_files_btn = QPushButton("Clear All")
        clear_files_btn.clicked.connect(self.clear_convert_files)

        button_layout.addWidget(add_files_btn)
        button_layout.addWidget(remove_file_btn)
        button_layout.addWidget(clear_files_btn)
        file_layout.addLayout(button_layout)

        layout.addWidget(file_group)

        # Conversion settings group
        settings_group = QGroupBox("Conversion Settings")
        settings_layout = QFormLayout(settings_group)

        # From format
        self.convert_from_combo = QComboBox()
        self.convert_from_combo.addItems(["pdf", "image"])
        self.convert_from_combo.setCurrentText("pdf")
        settings_layout.addRow("From:", self.convert_from_combo)

        # To format
        self.convert_to_combo = QComboBox()
        self.convert_to_combo.addItems(["pdf", "image"])
        self.convert_to_combo.setCurrentText("image")
        settings_layout.addRow("To:", self.convert_to_combo)

        # Output format (for PDF to image)
        self.convert_output_format_combo = QComboBox()
        self.convert_output_format_combo.addItems(["png", "jpg", "jpeg", "bmp", "tiff", "webp"])
        self.convert_output_format_combo.setCurrentText("png")
        settings_layout.addRow("Image Format:", self.convert_output_format_combo)

        # DPI
        self.convert_dpi_spin = QSpinBox()
        self.convert_dpi_spin.setRange(72, 600)
        self.convert_dpi_spin.setValue(200)
        settings_layout.addRow("DPI:", self.convert_dpi_spin)

        # Output file
        self.convert_output_edit = QLineEdit("converted_output")
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_convert_output)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.convert_output_edit)
        output_layout.addWidget(output_browse_btn)

        settings_layout.addRow("Output Base Name:", output_layout)
        layout.addWidget(settings_group)

        # Progress bar
        self.convert_progress = QProgressBar()
        self.convert_progress.setVisible(False)
        layout.addWidget(self.convert_progress)

        # Convert button
        self.convert_btn = QPushButton("Convert Files")
        self.convert_btn.clicked.connect(self.convert_files)
        layout.addWidget(self.convert_btn)

        self.tab_widget.addTab(tab, "Convert")
