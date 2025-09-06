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
            elif self.operation == "image_to_pdf":
                self.pdf_tools.image_to_pdf(*self.args, **self.kwargs)
            elif self.operation == "pdf_to_image":
                self.pdf_tools.pdf_to_image(*self.args, **self.kwargs)

            self.finished.emit("Operation completed successfully!")

        except Exception as e:
            logger.error(f"Operation failed: {e}")
            self.error.emit(str(e))


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
        self.create_image_to_pdf_tab()
        self.create_pdf_to_image_tab()

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

    def create_image_to_pdf_tab(self):
        """Create the image to PDF tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Image files group
        image_group = QGroupBox("Select Image Files")
        image_layout = QVBoxLayout(image_group)

        self.image_file_list = QListWidget()
        image_layout.addWidget(self.image_file_list)

        button_layout = QHBoxLayout()
        add_images_btn = QPushButton("Add Images")
        add_images_btn.clicked.connect(self.add_image_files)
        remove_image_btn = QPushButton("Remove Selected")
        remove_image_btn.clicked.connect(self.remove_image_file)
        clear_images_btn = QPushButton("Clear All")
        clear_images_btn.clicked.connect(self.clear_image_files)

        button_layout.addWidget(add_images_btn)
        button_layout.addWidget(remove_image_btn)
        button_layout.addWidget(clear_images_btn)
        image_layout.addLayout(button_layout)

        layout.addWidget(image_group)

        # Output settings group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout(output_group)

        self.image_to_pdf_output_edit = QLineEdit("output.pdf")
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_image_to_pdf_output)

        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.image_to_pdf_output_edit)
        output_path_layout.addWidget(output_browse_btn)

        output_layout.addRow("Output PDF:", output_path_layout)
        layout.addWidget(output_group)

        # Progress bar
        self.image_to_pdf_progress = QProgressBar()
        self.image_to_pdf_progress.setVisible(False)
        layout.addWidget(self.image_to_pdf_progress)

        # Convert button
        self.image_to_pdf_btn = QPushButton("Convert to PDF")
        self.image_to_pdf_btn.clicked.connect(self.convert_images_to_pdf)
        layout.addWidget(self.image_to_pdf_btn)

        self.tab_widget.addTab(tab, "Images to PDF")

    def create_pdf_to_image_tab(self):
        """Create the PDF to image tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Input file group
        input_group = QGroupBox("Input PDF File")
        input_layout = QFormLayout(input_group)

        self.pdf_to_image_input_edit = QLineEdit()
        input_browse_btn = QPushButton("Browse...")
        input_browse_btn.clicked.connect(self.browse_pdf_to_image_input)

        input_layout_h = QHBoxLayout()
        input_layout_h.addWidget(self.pdf_to_image_input_edit)
        input_layout_h.addWidget(input_browse_btn)

        input_layout.addRow("PDF File:", input_layout_h)
        layout.addWidget(input_group)

        # Settings group
        settings_group = QGroupBox("Conversion Settings")
        settings_layout = QFormLayout(settings_group)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(200)
        settings_layout.addRow("DPI:", self.dpi_spinbox)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpg", "jpeg", "tiff", "bmp"])
        settings_layout.addRow("Format:", self.format_combo)

        self.pdf_to_image_output_edit = QLineEdit()
        output_browse_btn = QPushButton("Browse...")
        output_browse_btn.clicked.connect(self.browse_pdf_to_image_output)

        output_layout_h = QHBoxLayout()
        output_layout_h.addWidget(self.pdf_to_image_output_edit)
        output_layout_h.addWidget(output_browse_btn)

        settings_layout.addRow("Output Folder:", output_layout_h)
        layout.addWidget(settings_group)

        # Progress bar
        self.pdf_to_image_progress = QProgressBar()
        self.pdf_to_image_progress.setVisible(False)
        layout.addWidget(self.pdf_to_image_progress)

        # Convert button
        self.pdf_to_image_btn = QPushButton("Convert to Images")
        self.pdf_to_image_btn.clicked.connect(self.convert_pdf_to_images)
        layout.addWidget(self.pdf_to_image_btn)

        self.tab_widget.addTab(tab, "PDF to Images")

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

    def add_image_files(self):
        """Add image files for PDF conversion"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            "Image Files (*.png *.jpg *.jpeg *.tiff *.bmp *.gif)",
        )
        for file in files:
            self.image_file_list.addItem(file)

    def remove_image_file(self):
        """Remove selected image file"""
        current_row = self.image_file_list.currentRow()
        if current_row >= 0:
            self.image_file_list.takeItem(current_row)

    def clear_image_files(self):
        """Clear all image files"""
        self.image_file_list.clear()

    def browse_image_to_pdf_output(self):
        """Browse for image to PDF output file"""
        file, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if file:
            self.image_to_pdf_output_edit.setText(file)

    def browse_pdf_to_image_input(self):
        """Browse for PDF to image input file"""
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file:
            self.pdf_to_image_input_edit.setText(file)
            # Auto-set output folder
            path = Path(file)
            output_folder = path.parent / f"{path.stem}_images"
            self.pdf_to_image_output_edit.setText(str(output_folder))

    def browse_pdf_to_image_output(self):
        """Browse for PDF to image output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.pdf_to_image_output_edit.setText(folder)

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

    def convert_images_to_pdf(self):
        """Start image to PDF conversion"""
        if self.image_file_list.count() == 0:
            QMessageBox.warning(self, "Warning", "Please select image files.")
            return

        output_file = self.image_to_pdf_output_edit.text()
        if not output_file:
            QMessageBox.warning(self, "Warning", "Please specify output PDF file.")
            return

        # Get image list
        images = []
        for i in range(self.image_file_list.count()):
            images.append(self.image_file_list.item(i).text())

        self.start_operation(
            "image_to_pdf",
            images,
            [],
            output_file,
            progress_bar=self.image_to_pdf_progress,
            button=self.image_to_pdf_btn,
        )

    def convert_pdf_to_images(self):
        """Start PDF to images conversion"""
        input_file = self.pdf_to_image_input_edit.text()
        output_folder = self.pdf_to_image_output_edit.text()
        dpi = self.dpi_spinbox.value()
        format_type = self.format_combo.currentText()

        if not input_file:
            QMessageBox.warning(self, "Warning", "Please select input PDF file.")
            return

        self.start_operation(
            "pdf_to_image",
            [input_file],
            output_folder,
            dpi,
            format_type,
            progress_bar=self.pdf_to_image_progress,
            button=self.pdf_to_image_btn,
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
        elif button == self.image_to_pdf_btn:
            button.setText("Convert to PDF")
        elif button == self.pdf_to_image_btn:
            button.setText("Convert to Images")
