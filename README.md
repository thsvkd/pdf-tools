# pdf-tools

Professional PDF processing tool collection with CLI and GUI interfaces

## Features

- **Merge PDFs**: Combine multiple PDF files into one
- **Compress PDFs**: Reduce PDF file sizes with quality options
- **Convert**: Unified conversion between PDF and images
  - PDF to images (PNG, JPG, etc.)
  - Images to PDF
- **GUI Application**: User-friendly Flet interface
- **Shell Completion**: Auto-completion for bash, zsh, and fish
- **Development Tools**: Pre-commit hooks for code quality

## Installation

### Using UV (Recommended)

```bash
# Global installation (recommended for CLI usage)
uv tool install .

# Development installation
uv sync --extra dev
```

### Using pip

```bash
# Development installation
pip install -e .

# Production installation
pip install .
```

## Dependencies

### Core Dependencies

- pdf2image
- tqdm
- Pillow
- PyPDF2
- click
- coloredlogs
- python-dotenv
- flet

### Development Dependencies

- ruff (linting & formatting)
- pre-commit (git hooks)

## Usage

### CLI Commands

#### Merge PDFs

```bash
pdf-tools merge <file1.pdf> <file2.pdf> ... [--output merged.pdf]
```

#### Compress PDF

```bash
pdf-tools compress <input.pdf> [--output output.pdf] [--quality printer]
```

#### Convert (Unified conversion command)

**Convert images to PDF:**

```bash
pdf-tools convert image1.jpg image2.png --from image --to pdf --output result
# Creates result.pdf
```

**Convert PDF to images:**

```bash
pdf-tools convert input.pdf --from pdf --to image --format png --dpi 200 --output output
# Creates output.png (single page) or output_page_*.png (multiple pages)
```

**Advanced conversion options:**

```bash
# Rotate specific images when creating PDF
pdf-tools convert img1.jpg img2.jpg --from image --to pdf --output rotated --rotate 0,90 --rotate 1,180

# Convert multiple PDFs to images
pdf-tools convert doc1.pdf doc2.pdf --from pdf --to image --format jpg --dpi 300 --output converted
```

#### GUI Application

```bash
pdf-tools gui
```

Launches a user-friendly graphical interface with tabs for merge, compress, and convert operations. The GUI is built with Flet, providing cross-platform support for web, desktop, and mobile.

#### Shell Completion

```bash
# Setup auto-completion for your shell
pdf-tools completion

# Or manually specify shell type
pdf-tools completion --shell zsh
```

### Development Usage

```bash
# Run from source
uv run pdf-tools --help

# Install pre-commit hooks
pre-commit install

# Format code
ruff format .

# Lint code
ruff check .
```

## Notes

- **Korean Font Support**: Korean fonts are required for Korean PDF conversion. Install with:

  ```bash
  sudo apt-get update
  sudo apt-get install fonts-nanum
  fc-cache -f -v
  ```

- **Multiple File Processing**: You can convert multiple PDF files at once. A separate folder is created for each PDF.

- **Python Version**: Python 3.10 or higher is required.

- **Development Setup**: This project uses pre-commit hooks for code quality. Run `pre-commit install` after cloning.

## Project Structure

```text
pdf-tools/
├── pdf_tools/           # Main package
│   ├── common/         # Shared utilities and enums
│   ├── gui/           # Flet GUI application
│   └── __main__.py    # CLI entry point
├── scripts/           # Development scripts
├── pyproject.toml     # Project configuration
└── .pre-commit-config.yaml  # Code quality hooks
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `uv sync`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes
6. Run tests and linting: `ruff check . && ruff format .`
7. Commit your changes (pre-commit hooks will run automatically)
8. Submit a pull request
