import os
import re
import time
import subprocess
from pdf2image import convert_from_path
from pathlib import Path
from typing import Optional

from tqdm import tqdm
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


class ProgressBar:
    """
    진행바를 관리하는 클래스
    """
    def __init__(self, total: int, desc: str, unit: str, bar_format: str):
        self.pbar = tqdm(total=total, desc=desc, unit=unit, bar_format=bar_format)

    def update(self, n: int = 1):
        self.pbar.update(n)

    def close(self):
        self.pbar.close()


class PDFTools:
    """
    PDF 관련 도구들을 모은 클래스
    """

    def __init__(self):
        pass

    def get_ext_files(self, root: str, ext: str) -> list[str]:
        """
        지정된 루트 디렉토리에서 특정 확장자의 파일들을 재귀적으로 찾음

        Args:
            root (str): 검색할 루트 디렉토리 경로
            ext (str): 찾을 파일 확장자 (예: '.pdf')

        Returns:
            list[str]: 찾은 파일 경로 리스트
        """
        return [str(p) for p in Path(root).rglob(f"*{ext}")]

    def rename_files_in_directory(self, directory_path: str, dry_run: bool = False):
        """
        지정된 디렉토리의 파일들을 새로운 형식으로 이름 변경
        dry_run이 True이면 실제 변경 없이 변경될 내용을 출력

        Args:
            directory_path (str): 파일들이 있는 디렉토리 경로
            dry_run (bool): 실제 변경 없이 출력할지 여부
        """
        for filename in os.listdir(directory_path):
            if filename.endswith(".pdf"):
                # 날짜 패턴 찾기
                match = re.search(r"(\d{4}-\d{2}-\d{2})__(\d{4}-\d{2}-\d{2})", filename)
                if match:
                    start_date = match.group(1)
                    end_date = match.group(2)
                    new_filename = f"{start_date} ~ {end_date}.pdf"

                    old_path = os.path.join(directory_path, filename)
                    new_path = os.path.join(directory_path, new_filename)

                    if dry_run:
                        print(f"[드라이 런] 변경될 예정: {filename} -> {new_filename}")
                    else:
                        # 파일명 변경
                        os.rename(old_path, new_path)
                        print(f"변경됨: {filename} -> {new_filename}")

    def merge_pdf(
        self,
        pdf_files: list[str],
        output_path: str = "merged_output.pdf",
        uniform_size: tuple[float, float] = (595.276, 841.89)
    ):
        """
        스트림 기반으로 PDF를 빠르게 병합하는 함수, 페이지 크기를 통일시킴

        Args:
            pdf_files (list[str]): 병합할 PDF 파일 경로 리스트
            output_path (str): 병합된 PDF의 출력 경로 (기본값: 'merged_output.pdf')
            uniform_size (tuple[float, float]): 통일할 페이지 크기 (너비, 높이) in 포인트 (기본: A4)

        Returns:
            None
        """
        if not pdf_files:
            print("병합할 PDF 파일이 없습니다.")
            return

        # 파일 존재 여부 일괄 확인
        missing_files = [f for f in pdf_files if not os.path.exists(f)]
        if missing_files:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {missing_files}")

        writer = PdfWriter()

        try:
            start_time = time.time()

            # 스트림 기반으로 빠르게 병합, 페이지 크기 통일
            total_files = len(pdf_files)
            pbar = ProgressBar(total_files, "🔄 PDF 병합 중", "file", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}")
            for pdf_file in pdf_files:
                print(f"병합 중: {pdf_file}")

                with open(pdf_file, "rb") as f:
                    reader = PdfReader(f)

                    # 각 페이지를 통일된 크기로 조정
                    for page in reader.pages:
                        # 페이지 크기 통일 (스케일링)
                        page.scale_to(width=uniform_size[0], height=uniform_size[1])
                        writer.add_page(page)
                pbar.update(1)
            pbar.close()

            # 한 번에 쓰기
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            elapsed_time = time.time() - start_time
            print(f"✅ 병합 완료! 파일이 저장되었습니다: {output_path}")
            print(f"⏱️ 소요 시간: {elapsed_time:.2f}초")
            print(f"📐 페이지 크기 통일: {uniform_size[0]}x{uniform_size[1]} 포인트 (A4)")

        except Exception as e:
            print(f"❌ 병합 중 오류가 발생했습니다: {e}")

    def compress_pdf(self, input_path: str, output_path: str = None, quality: str = "printer"):
        """
        Ghostscript를 사용한 고성능 PDF 압축 함수 (진행바 포함)

        Args:
            input_path (str): 원본 PDF 파일 경로
            output_path (str): 압축된 PDF 출력 경로 (None시 자동생성)
            quality (str): 압축 품질 설정

        Returns:
            tuple: (성공여부, 압축률, 메시지)
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

            # 진행바 설정
            pbar = ProgressBar(100, "🔄 PDF 압축 중", "%", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}")

            # subprocess를 별도 스레드에서 실행
            process = subprocess.Popen(gs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # 진행바 업데이트 (파일 크기 기반 추정)
            while process.poll() is None:
                # 출력 파일이 생성되기 시작하면 크기 확인
                if os.path.exists(output_path):
                    try:
                        current_size = os.path.getsize(output_path)
                        # 대략적인 진행률 계산 (압축률 고려)
                        progress = min(95, (current_size / (original_size * 0.5)) * 100)
                        pbar.update(progress - pbar.pbar.n)
                    except Exception:
                        pass
                else:
                    # 파일이 아직 생성되지 않은 경우 시간 기반 진행
                    elapsed = time.time() - start_time
                    progress = min(30, elapsed * 10)  # 최대 30%까지
                    pbar.update(progress - pbar.pbar.n)

                time.sleep(0.1)

            # 완료 처리
            pbar.update(100 - pbar.pbar.n)
            pbar.close()

            # 에러 확인
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                return False, 0, f"Ghostscript 실행 오류: {stderr}"

            # 압축된 파일 크기
            compressed_size = os.path.getsize(output_path)
            compression_ratio = ((original_size - compressed_size) / original_size) * 100

            elapsed_time = time.time() - start_time

            print("\n✅ PDF 압축 완료!")
            print(f"📁 원본 크기: {original_size / 1024 / 1024:.2f} MB")
            print(f"📦 압축 후: {compressed_size / 1024 / 1024:.2f} MB")
            print(f"📉 압축률: {compression_ratio:.1f}% 감소")
            print(f"⏱️ 소요 시간: {elapsed_time:.2f}초")
            print(f"💾 저장 위치: {output_path}")

            return True, compression_ratio, "압축 성공"

        except subprocess.CalledProcessError as e:
            return False, 0, f"Ghostscript 실행 오류: {e}"
        except Exception as e:
            return False, 0, f"압축 중 오류: {e}"

    def image_to_pdf(self, image_files: list[str], rotate: list[tuple[int, int]] = [], output_path: str = "output.pdf"):
        """
        이미지 파일들을 PDF로 변환하는 함수 (JPEG, PNG 등 지원)

        Args:
            image_files (list[str]): 이미지 파일 경로의 리스트 (JPEG, PNG 등)
            rotate (list[tuple[int, int]]): (이미지 파일의 인덱스, 회전 각도) 튜플의 리스트
            output_path (str): 출력 PDF 파일 경로 (기본값: 'output.pdf')

        Returns:
            None
        """
        try:
            images = []
            # 회전 딕셔너리로 변환 (인덱스: 회전 각도)
            rotate_dict = {idx: angle for idx, angle in rotate}

            total_images = len(image_files)
            pbar = ProgressBar(total_images, "🔄 이미지를 PDF로 변환 중", "image", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}")
            for i, file_path in enumerate(image_files):
                # 이미지 파일 열기 (PIL이 지원하는 형식)
                img = Image.open(file_path)

                # 회전 필요하면 수행
                if i in rotate_dict:
                    angle = rotate_dict[i]
                    # 시계 반대 방향으로 회전 (PIL 기본)
                    img = img.rotate(angle, expand=True)  # expand=True로 크기 자동조절

                # RGB 모드로 변환 (PDF 저장시 필요)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                images.append(img)
                pbar.update(1)
            pbar.close()

            # 첫 이미지를 기준으로 나머지를 추가하여 PDF 저장
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
                print(f"PDF 파일이 생성되었습니다: {output_path}")
            else:
                print("입력된 이미지 파일이 없습니다.")

        except FileNotFoundError as e:
            print(f"파일을 찾을 수 없습니다: {e}")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")

    def pdf_to_image(self, pdf_path: str, output_folder: Optional[str] = None, dpi: int = 200, format: str = "png"):
        """
        PDF 파일을 이미지로 변환하는 함수

        Args:
            pdf_path (str): 변환할 PDF 파일 경로
            output_folder (str): 이미지가 저장될 폴더 경로
            dpi (int): 변환 시 해상도 (기본값: 200)
            format (str): 출력 이미지 형식 (기본값: 'png')

        Returns:
            list: 생성된 이미지 파일 경로 리스트
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

        if output_folder is None:
            output_folder = os.path.splitext(pdf_path)[0] + "_images"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        try:
            # PDF를 이미지로 변환
            images = convert_from_path(pdf_path, dpi=dpi)
            image_paths = []

            pbar = ProgressBar(len(images), "🔄 PDF를 이미지로 변환 중", "page", "{desc}: {percentage:3.0f}%|{bar}| {elapsed}")
            for i, image in enumerate(images):
                image_path = os.path.join(output_folder, f"page_{i + 1}.{format}")
                image.save(image_path, format.upper())
                image_paths.append(image_path)
                pbar.update(1)
            pbar.close()

            print(f"✅ PDF가 {format.upper()} 이미지로 변환되었습니다. 총 {len(image_paths)}장 생성됨.")
            return image_paths

        except Exception as e:
            print(f"❌ PDF 변환 중 오류가 발생했습니다: {e}")
            return []


# 사용 예시
if __name__ == "__main__":
    tools = PDFTools()

    # 예시: PDF 병합
    # pdf_list = tools.get_ext_files("/path/to/pdfs", ".pdf")
    # tools.merge_pdf(pdf_list, "merged.pdf")

    # 예시: PDF 압축
    # tools.compress_pdf("input.pdf", "output.pdf")

    # 예시: 이미지에서 PDF 생성
    # image_files = ["image1.jpg", "image2.png"]
    # tools.image_to_pdf(image_files, output_path="output.pdf")

    # 예시: PDF에서 이미지 변환
    # tools.pdf_to_image("input.pdf", "./images", dpi=300)