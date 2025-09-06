# PDF Tools
PDF Tools is a Python CLI application for processing PDF files including merge, compress, image conversion, and rename functionality. It uses modern Python packaging with pyproject.toml and provides a Click-based command-line interface.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### System Dependencies
- Install required system packages:
  ```bash
  sudo apt-get update
  sudo apt-get install -y ghostscript poppler-utils fonts-nanum
  fc-cache -f -v
  ```
- **TIMING**: apt-get update takes ~10 seconds, package installation takes ~30 seconds
- **CRITICAL**: Ghostscript is required for PDF compression, poppler-utils for PDF to image conversion
- Korean fonts (fonts-nanum) are required for Korean PDF processing

### Python Environment Setup
- **Python Version**: Requires Python 3.8 or higher (project tested with Python 3.12)
- Install dependencies using pip (UV may not be accessible due to network restrictions):
  ```bash
  pip3 install -e .
  ```
- **TIMING**: Installation takes ~15 seconds. NEVER CANCEL - Set timeout to 60+ seconds
- **NETWORK ISSUE**: Standard `pip install .` may fail due to network timeouts when downloading build dependencies. Use `pip install -e .` for development

### Build and Installation
- **Editable Installation** (recommended for development):
  ```bash
  cd /path/to/pdf-tools
  pip3 install -e .
  ```
- **TIMING**: Takes ~15 seconds, NEVER CANCEL
- **Package Verification**: Check installation with `pdf-tools --help`

## Core Dependencies
The following dependencies are automatically installed:
- **pdf2image**: PDF to image conversion (requires poppler-utils)
- **tqdm**: Progress bars
- **Pillow**: Image processing
- **PyPDF2**: PDF manipulation
- **coloredlogs**: Colored logging output
- **python-dotenv**: Environment configuration
- **click**: CLI framework

## Validation and Testing

### Linting and Formatting
- **Ruff Installation**:
  ```bash
  pip3 install ruff
  ```
- **Linting** (check code style):
  ```bash
  ruff check .
  ```
- **TIMING**: Linting takes ~0.01 seconds
- **Formatting** (check format):
  ```bash
  ruff format --check .
  ```
- **TIMING**: Format checking takes ~0.01 seconds
- **Auto-fix** (apply formatting):
  ```bash
  ruff format .
  ```
- **ALWAYS** run `ruff check .` and `ruff format --check .` before committing changes

### Testing Functionality
**MANUAL VALIDATION REQUIREMENT**: Always test actual functionality after making changes:

1. **Create test directory and sample files**:
   ```bash
   mkdir -p /tmp/pdf-test && cd /tmp/pdf-test
   ```

2. **Create test images**:
   ```python
   python3 -c "
   from PIL import Image, ImageDraw
   for i in range(3):
       img = Image.new('RGB', (400, 300), color=(100 + i*50, 150, 200))
       draw = ImageDraw.Draw(img)
       draw.text((50, 50), f'Test Image {i+1}', fill=(255, 255, 255))
       draw.rectangle([50, 100, 350, 200], outline=(255, 0, 0), width=3)
       img.save(f'test_image_{i+1}.png')
   "
   ```

3. **Test all core functionality**:
   ```bash
   # Image to PDF conversion (~0.16s)
   pdf-tools image-to-pdf test_image_1.png test_image_2.png test_image_3.png --output test.pdf
   
   # PDF to image conversion (~0.41s)
   pdf-tools pdf-to-image test.pdf --output images --dpi 150 --format png
   
   # PDF merging (~0.13s)
   cp test.pdf test2.pdf
   pdf-tools merge test.pdf test2.pdf --output merged.pdf
   
   # PDF compression (~0.23s)
   pdf-tools compress merged.pdf --output compressed.pdf --quality printer
   ```

4. **Verify outputs**:
   ```bash
   ls -la *.pdf
   ls -la images/
   ```

## CLI Commands Reference

### Available Commands
- `pdf-tools --help` - Show all available commands
- `pdf-tools merge` - Merge multiple PDF files
- `pdf-tools compress` - Compress PDF using Ghostscript
- `pdf-tools image-to-pdf` - Convert images to PDF
- `pdf-tools pdf-to-image` - Convert PDF to images
- `pdf-tools completion` - Setup shell completion

### Command Examples
```bash
# Merge PDFs
pdf-tools merge file1.pdf file2.pdf --output merged.pdf

# Compress PDF (quality options: screen, ebook, printer, prepress)
pdf-tools compress input.pdf --output compressed.pdf --quality printer

# Convert images to PDF with rotation
pdf-tools image-to-pdf img1.jpg img2.png --output output.pdf --rotate 0,90

# Convert PDF to images with custom DPI
pdf-tools pdf-to-image input.pdf --output images/ --dpi 300 --format png
```

## Project Structure
```
pdf_tools/
├── __init__.py              # Empty module init
├── __main__.py             # CLI entry point with Click commands
├── pdf_tools.py            # Core PDFTools class with all functionality
└── common/
    ├── utils.py            # Utility functions (file operations)
    └── helper/
        └── progress_bar.py # Progress bar wrapper for tqdm
```

## Configuration
- **Environment Variables**: Copy `.env.example` to `.env` for custom logging configuration
- **Log Level**: Set `LOG_LEVEL=INFO` (default) or `DEBUG`
- **Log Path**: Set `LOG_PATH=/path/to/log/file` (default: `~/pdf_tools/pdf_tools.log`)
- **VS Code**: Configuration in `.vscode/settings.json` with Ruff formatting enabled

## Common Issues and Solutions

### Network Timeouts
- Use `pip install -e .` instead of `pip install .` for development
- Standard installation may fail due to network restrictions when downloading build dependencies

### Missing System Dependencies
- **Error**: "gs: command not found" → Install ghostscript: `sudo apt-get install ghostscript`
- **Error**: "pdf2image conversion failed" → Install poppler: `sudo apt-get install poppler-utils`
- **Korean PDF issues** → Install fonts: `sudo apt-get install fonts-nanum && fc-cache -f -v`

### Linting Issues
- **Line length**: Ruff enforces 88-character line limit (configured in pyproject.toml)
- **Import order**: Ruff automatically organizes imports according to isort rules
- **Auto-fix most issues**: `ruff check --fix .`

## Timing Expectations
- **System setup**: 60-90 seconds total for all dependencies
- **Python package installation**: 15 seconds with `pip install -e .`
- **Linting/formatting**: < 0.1 seconds
- **PDF operations**: 0.1-0.5 seconds for typical files
- **Font cache refresh**: ~5 seconds

**NEVER CANCEL**: Always wait for operations to complete. Set timeouts to 60+ seconds for installation, 30+ seconds for PDF processing.

## Key Development Workflows

### Making Changes
1. Make code changes
2. Run linting: `ruff check .`
3. Run formatting: `ruff format --check .`
4. Test functionality with sample files (see Testing section)
5. Verify all CLI commands work correctly

### Debugging
- Enable debug logging: Set `LOG_LEVEL=DEBUG` in environment
- Check log file at `~/pdf_tools/pdf_tools.log`
- Use `pdf-tools --help` to verify CLI is properly installed
- Test with simple single-file operations first

This repository does not have automated tests, so manual validation is essential for ensuring changes work correctly.