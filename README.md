# pdf-tools

PDF 처리 도구 모음

## 기능

- PDF 파일 이름 변경
- PDF 병합
- PDF 압축
- 이미지에서 PDF 생성
- PDF에서 이미지 변환 (여러 파일 지원)

## 설치

```bash
pip install -e .
```

또는

```bash
python -m pip install .
```

## 의존성

- pdf2image
- tqdm
- Pillow
- PyPDF2

## 사용법

### PDF 파일 이름 변경

```bash
pdf-tools rename <directory> [--dry-run]
```

### PDF 병합

```bash
pdf-tools merge <file1.pdf> <file2.pdf> ... [--output merged.pdf]
```

### PDF 압축

```bash
pdf-tools compress <input.pdf> [--output output.pdf] [--quality printer]
```

### 이미지에서 PDF 생성

```bash
pdf-tools image-to-pdf <image1.jpg> <image2.png> ... [--output output.pdf] [--rotate idx,angle]
```

### PDF에서 이미지 변환

```bash
pdf-tools pdf-to-image <input.pdf> ... [--output output_dir] [--dpi 200] [--format png]
```

or

```bash
pdf-tools pdf-to-image <pdf1.pdf> <pdf2.pdf> ... [--output output_dir] [--dpi 200] [--format png]
# 여러 PDF 파일을 동시에 변환할 수 있습니다. 각 PDF에 대해 별도의 폴더가 생성됩니다.
```

## 유의 사항

- 한글 PDF 변환 시 한글 폰트가 필요합니다. 다음 명령으로 설치하세요:

  ```bash
  sudo apt-get update
  sudo apt-get install fonts-nanum
  fc-cache -f -v
  ```

- 여러 PDF 파일을 동시에 변환할 수 있습니다. 각 PDF에 대해 별도의 폴더가 생성됩니다.

- Python 3.8 이상이 필요합니다.
