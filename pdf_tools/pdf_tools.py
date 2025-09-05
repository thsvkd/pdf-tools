import os
import time
import subprocess
from typing import Optional

from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path

from .common.helper.progress_bar import ProgressBar


class PDFTools:
    """
    A class that collects PDF-related tools
    """

    def __init__(self):
        pass

    def merge_pdf(
        self,
        pdf_files: list[str],
        output_path: str = "merged_output.pdf",
        uniform_size: tuple[float, float] = (595.276, 841.89)
    ):
        """
        A function to quickly merge PDFs based on streams, unifying page sizes

        Args:
            pdf_files (list[str]): List of PDF file paths to merge
            output_path (str): Output path for the merged PDF (default: 'merged_output.pdf')
            uniform_size (tuple[float, float]): Uniform page size (width, height) in points (default: A4)

        Returns:
            None
        """
        if not pdf_files:
            print("병합할 PDF 파일이 없습니다.")
            return

        # Check file existence in batch
        missing_files = [f for f in pdf_files if not os.path.exists(f)]
        if missing_files:
            raise FileNotFoundError(f"Files not found: {missing_files}")

        writer = PdfWriter()

        try:
            start_time = time.time()

            # Quickly merge based on streams, unify page sizes
            total_files = len(pdf_files)
            with ProgressBar(total_files, "🔄 Merging PDFs", "file", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}") as pbar:
                for pdf_file in pdf_files:
                    print(f"Merging: {pdf_file}")

                    with open(pdf_file, "rb") as f:
                        reader = PdfReader(f)

                        # Adjust each page to uniform size
                        for page in reader.pages:
                            # Unify page size (scaling)
                            page.scale_to(width=uniform_size[0], height=uniform_size[1])
                            writer.add_page(page)
                    pbar.update(1)

            # Write at once
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            elapsed_time = time.time() - start_time
            print(f"✅ Merge completed! File saved at: {output_path}")
            print(f"⏱️ Elapsed time: {elapsed_time:.2f}s")
            print(f"📐 Page size unified: {uniform_size[0]}x{uniform_size[1]} points (A4)")

        except Exception as e:
            print(f"❌ Error occurred during merging: {e}")

    def compress_pdf(self, input_path: str, output_path: str = None, quality: str = "printer"):
        """
        High-performance PDF compression function using Ghostscript (with progress bar)

        Args:
            input_path (str): Original PDF file path
            output_path (str): Compressed PDF output path (auto-generated if None)
            quality (str): Compression quality setting

        Returns:
            tuple: (success, compression_ratio, message)
        """
        if not os.path.exists(input_path):
            return False, 0, f"입력 파일이 존재하지 않습니다: {input_path}"

        if output_path is None:
            name, ext = os.path.splitext(input_path)
            output_path = f"{name}_compressed{ext}"

        # 원본 파일 크기
        original_size = os.path.getsize(input_path)

        gs_command = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            "-dAutoRotatePages=/None",
            "-dColorImageDownsampleType=/Bicubic",
            "-dGrayImageDownsampleType=/Bicubic",
            "-dMonoImageDownsampleType=/Subsample",
            "-dEmbedAllFonts=true",
            "-dSubsetFonts=true",
            f"-sOutputFile={output_path}",
            input_path,
        ]

        try:
            start_time = time.time()

            # Set up progress bar
            with ProgressBar(100, "🔄 Compressing PDF", "%", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}") as pbar:
                # Run subprocess in a separate thread
                process = subprocess.Popen(gs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Update progress bar (estimated based on file size)
                while process.poll() is None:
                    # Check size when output file starts to be created
                    if os.path.exists(output_path):
                        try:
                            current_size = os.path.getsize(output_path)
                            # Calculate approximate progress (considering compression ratio)
                            progress = min(95, (current_size / (original_size * 0.5)) * 100)
                            pbar.update(progress - pbar.pbar.n)
                        except Exception:
                            pass
                    else:
                        # Time-based progress if file not yet created
                        elapsed = time.time() - start_time
                        progress = min(30, elapsed * 10)  # Up to 30%
                        pbar.update(progress - pbar.pbar.n)

                    time.sleep(0.1)

                # Completion processing
                pbar.update(100 - pbar.pbar.n)

            # Check for errors
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                return False, 0, f"Ghostscript execution error: {stderr}"

            # Compressed file size
            compressed_size = os.path.getsize(output_path)
            compression_ratio = ((original_size - compressed_size) / original_size) * 100

            elapsed_time = time.time() - start_time

            print("\n✅ PDF compression completed!")
            print(f"📁 Original size: {original_size / 1024 / 1024:.2f} MB")
            print(f"📦 After compression: {compressed_size / 1024 / 1024:.2f} MB")
            print(f"📉 Compression ratio: {compression_ratio:.1f}% reduction")
            print(f"⏱️ Elapsed time: {elapsed_time:.2f}s")
            print(f"💾 Saved at: {output_path}")

            return True, compression_ratio, "Compression successful"

        except subprocess.CalledProcessError as e:
            return False, 0, f"Ghostscript execution error: {e}"
        except Exception as e:
            return False, 0, f"Error during compression: {e}"

    def image_to_pdf(self, image_files: list[str], rotate: list[tuple[int, int]] = [], output_path: str = "output.pdf"):
        """
        Function to convert image files to PDF (supports JPEG, PNG, etc.)

        Args:
            image_files (list[str]): List of image file paths (JPEG, PNG, etc.)
            rotate (list[tuple[int, int]]): List of tuples (image file index, rotation angle)
            output_path (str): Output PDF file path (default: 'output.pdf')

        Returns:
            None
        """
        try:
            images = []
            # Convert to rotation dictionary (index: rotation angle)
            rotate_dict = {idx: angle for idx, angle in rotate}

            total_images = len(image_files)
            with ProgressBar(total_images, "🔄 Converting images to PDF", "image", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}") as pbar:
                for i, file_path in enumerate(image_files):
                    # Open image file (format supported by PIL)
                    img = Image.open(file_path)

                    # Perform rotation if needed
                    if i in rotate_dict:
                        angle = rotate_dict[i]
                        # Rotate counterclockwise (PIL default)
                        img = img.rotate(angle, expand=True)  # Auto-adjust size with expand=True

                    # Convert to RGB mode (required for PDF saving)
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    images.append(img)
                    pbar.update(1)

            # Save as PDF by appending the rest based on the first image
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
                print(f"PDF file created: {output_path}")
            else:
                print("No input image files.")

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")

    def pdf_to_image(self, pdf_paths: list[str], output_folder: Optional[str] = None, dpi: int = 200, format: str = "png"):
        """
        Function to convert PDF files to images

        Args:
            pdf_paths (list[str]): List of PDF file paths to convert
            output_folder (str): Base folder path where images will be saved (auto-generate per PDF if None)
            dpi (int): Resolution during conversion (default: 200)
            format (str): Output image format (default: 'png')

        Returns:
            dict: Dictionary of generated image file path lists for each PDF
        """
        results = {}
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                print(f"❌ PDF file not found: {pdf_path}")
                continue

            # Determine output folder for each PDF
            if output_folder is None:
                pdf_folder = os.path.splitext(pdf_path)[0] + "_images"
            else:
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                pdf_folder = os.path.join(output_folder, pdf_name + "_images")

            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)

            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path, dpi=dpi, use_pdftocairo=True)
                image_paths = []

                with ProgressBar(
                    len(images), f"🔄 Converting {os.path.basename(pdf_path)}", "page", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}"
                ) as pbar:
                    for i, image in enumerate(images):
                        image_path = os.path.join(pdf_folder, f"page_{i + 1}.{format}")
                        image.save(image_path, format.upper())
                        image_paths.append(image_path)
                        pbar.update(1)

                results[pdf_path] = image_paths
                print(
                    f"✅ {os.path.basename(pdf_path)} converted to {format.upper()} images. Total {len(image_paths)} images created. Folder: {pdf_folder}"
                )

            except Exception as e:
                print(f"❌ Error occurred during conversion of {os.path.basename(pdf_path)}: {e}")
                results[pdf_path] = []

        return results


# Usage examples
if __name__ == "__main__":
    tools = PDFTools()

    # Example: PDF merging
    # pdf_list = tools.get_ext_files("/path/to/pdfs", ".pdf")
    # tools.merge_pdf(pdf_list, "merged.pdf")

    # Example: PDF compression
    # tools.compress_pdf("input.pdf", "output.pdf")

    # Example: Create PDF from images
    # image_files = ["image1.jpg", "image2.png"]
    # tools.image_to_pdf(image_files, output_path="output.pdf")

    # Example: Convert PDF to images
    # tools.pdf_to_image("input.pdf", "./images", dpi=300)