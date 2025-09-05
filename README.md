# pdf-tools

PDF processing tool collection

## Features

- Rename PDF files
- Merge PDFs
- Compress PDFs
- Create PDF from images
- Convert PDF to images (multiple files supported)

## Installation

```bash
pip install -e .
```

or

```bash
python -m pip install .
```

## Dependencies

- pdf2image
- tqdm
- Pillow
- PyPDF2

## Usage

### Rename PDF files

```bash
pdf-tools rename <directory> [--dry-run]
```

### Merge PDFs

```bash
pdf-tools merge <file1.pdf> <file2.pdf> ... [--output merged.pdf]
```

### Compress PDF

```bash
pdf-tools compress <input.pdf> [--output output.pdf] [--quality printer]
```

### Create PDF from images

```bash
pdf-tools image-to-pdf <image1.jpg> <image2.png> ... [--output output.pdf] [--rotate idx,angle]
```

### Convert PDF to images

```bash
pdf-tools pdf-to-image <input.pdf> ... [--output output_dir] [--dpi 200] [--format png]
```

or

```bash
pdf-tools pdf-to-image <pdf1.pdf> <pdf2.pdf> ... [--output output_dir] [--dpi 200] [--format png]
# You can convert multiple PDF files at once. A separate folder is created for each PDF.
```

## Notes

- Korean fonts are required for Korean PDF conversion. Install with the following commands:

  ```bash
  sudo apt-get update
  sudo apt-get install fonts-nanum
  fc-cache -f -v
  ```

- You can convert multiple PDF files at once. A separate folder is created for each PDF.

- Python 3.8 or higher is required.
