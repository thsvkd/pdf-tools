import argparse
from .pdf_tools import PDFTools


def main():
    parser = argparse.ArgumentParser(description="PDF Tools CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # rename command
    rename_parser = subparsers.add_parser('rename', help='Rename PDF files in directory')
    rename_parser.add_argument('directory', help='Directory path')
    rename_parser.add_argument('--dry-run', action='store_true', help='Dry run')

    # merge command
    merge_parser = subparsers.add_parser('merge', help='Merge PDF files')
    merge_parser.add_argument('files', nargs='+', help='PDF files to merge')
    merge_parser.add_argument('--output', '-o', default='merged.pdf', help='Output file')

    # compress command
    compress_parser = subparsers.add_parser('compress', help='Compress PDF')
    compress_parser.add_argument('input', help='Input PDF')
    compress_parser.add_argument('--output', '-o', help='Output PDF')
    compress_parser.add_argument('--quality', default='printer', help='Quality')

    # image-to-pdf command
    itp_parser = subparsers.add_parser('image-to-pdf', help='Convert images to PDF')
    itp_parser.add_argument('images', nargs='+', help='Image files')
    itp_parser.add_argument('--output', '-o', default='output.pdf', help='Output PDF')
    itp_parser.add_argument('--rotate', nargs='*', help='Rotate list (format: idx,angle)')

    # pdf-to-image command
    pti_parser = subparsers.add_parser('pdf-to-image', help='Convert PDF to images')
    pti_parser.add_argument('pdf', nargs='+', help='PDF files')
    pti_parser.add_argument('--output', '-o', help='Output folder (if not specified, creates folder per PDF)')
    pti_parser.add_argument('--dpi', type=int, default=200, help='DPI')
    pti_parser.add_argument('--format', default='png', help='Image format')

    args = parser.parse_args()

    tools = PDFTools()

    if args.command == 'rename':
        tools.rename_files_in_directory(args.directory, args.dry_run)
    elif args.command == 'merge':
        tools.merge_pdf(args.files, args.output)
    elif args.command == 'compress':
        tools.compress_pdf(args.input, args.output, args.quality)
    elif args.command == 'image-to-pdf':
        rotate_list = []
        if args.rotate:
            for r in args.rotate:
                idx, angle = map(int, r.split(','))
                rotate_list.append((idx, angle))
        tools.image_to_pdf(args.images, rotate_list, args.output)
    elif args.command == 'pdf-to-image':
        tools.pdf_to_image(args.pdf, args.output, args.dpi, args.format)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()