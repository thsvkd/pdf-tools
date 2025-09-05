import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import click
import coloredlogs
from dotenv import load_dotenv

from .common.pdf_tools import PDFTools


def setup_file_logging():
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH = os.getenv("LOG_PATH", "~/pdf_tools/pdf_tools.log").replace("~", str(Path.home()))

    """File logging setup - works alongside existing console logging"""
    # Coloredlogs configuration (for console output)
    coloredlogs.install(
        level=os.getenv("LOG_LEVEL", LOG_LEVEL),
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level_styles={
            "debug": {"color": "cyan"},
            "info": {"color": "green"},
            "warning": {"color": "yellow", "bold": True},
            "error": {"color": "red", "bold": True},
            "critical": {"color": "magenta", "bold": True},
        },
        field_styles={
            "asctime": {"color": "blue"},
            "name": {"color": "cyan"},
            "levelname": {"color": "white", "bold": True},
            "message": {"color": "white"},
        },
    )

    # Create log directory
    os.makedirs(Path(LOG_PATH).parent, exist_ok=True)

    # Add file handler to root logger
    root_logger = logging.getLogger()

    # Check if existing file handler exists (to prevent duplicates)
    file_handlers = [h for h in root_logger.handlers if isinstance(h, RotatingFileHandler)]
    if file_handlers:
        return

    # File handler that rotates in 100MB units
    file_handler = RotatingFileHandler(
        filename=LOG_PATH,
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding="utf-8",
    )

    # Set file log format
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Add to root logger
    root_logger.addHandler(file_handler)


load_dotenv()
setup_file_logging()


@click.group()
def cli():
    """PDF Tools CLI"""
    pass


@cli.command()
@click.argument("files", nargs=-1)
@click.option("--output", "-o", default="merged.pdf", help="Output file")
def merge(files, output):
    """Merge PDF files"""
    tools = PDFTools()
    tools.merge_pdf(list(files), output)


@cli.command()
@click.argument("input")
@click.option("--output", "-o", help="Output PDF")
@click.option("--quality", default="printer", help="Quality")
def compress(input, output, quality):
    """Compress PDF"""
    tools = PDFTools()
    tools.compress_pdf(input, output, quality)


@cli.command()
@click.argument("images", nargs=-1)
@click.option("--output", "-o", default="output.pdf", help="Output PDF")
@click.option("--rotate", multiple=True, help="Rotate list (format: idx,angle)")
def image_to_pdf(images, output, rotate):
    """Convert images to PDF"""
    rotate_list = []
    for r in rotate:
        idx, angle = map(int, r.split(","))
        rotate_list.append((idx, angle))
    tools = PDFTools()
    tools.image_to_pdf(list(images), rotate_list, output)


@cli.command()
@click.argument("pdf", nargs=-1)
@click.option("--output", "-o", help="Output folder (if not specified, creates folder per PDF)")
@click.option("--dpi", type=int, default=200, help="DPI")
@click.option("--format", default="png", help="Image format")
def pdf_to_image(pdf, output, dpi, format):
    """Convert PDF to images"""
    tools = PDFTools()
    tools.pdf_to_image(list(pdf), output, dpi, format)


@cli.command()
@click.option("--shell", type=click.Choice(["bash", "zsh", "fish"]), help="Shell type (if not specified, auto-detect)")
def completion(shell):
    """Setup shell completion for pdf-tools"""
    import subprocess

    # Auto-detect shell if not specified
    if not shell:
        shell_path = os.environ.get("SHELL", "")
        if "bash" in shell_path:
            shell = "bash"
        elif "zsh" in shell_path:
            shell = "zsh"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            click.echo("Could not auto-detect shell. Please specify --shell option.")
            return

    click.echo(f"Setting up completion for {shell}...")

    if shell == "bash":
        completion_script = "_PDF_TOOLS_COMPLETE=bash_source pdf-tools"
        click.echo("\nTo enable bash completion, run:")
        click.echo(f"  {completion_script} > ~/.pdf-tools-completion.bash")
        click.echo("  echo 'source ~/.pdf-tools-completion.bash' >> ~/.bashrc")

    elif shell == "zsh":
        completion_script = "_PDF_TOOLS_COMPLETE=zsh_source pdf-tools"
        click.echo("\nTo enable zsh completion, run:")
        click.echo(f"  {completion_script} > ~/.pdf-tools-completion.zsh")
        click.echo("  echo 'source ~/.pdf-tools-completion.zsh' >> ~/.zshrc")

    elif shell == "fish":
        completion_script = "_PDF_TOOLS_COMPLETE=fish_source pdf-tools"
        click.echo("\nTo enable fish completion, run:")
        click.echo(f"  {completion_script} > ~/.config/fish/completions/pdf-tools.fish")

    click.echo("\nOr run the following command to generate completion script:")
    click.echo(f"  {completion_script}")

    # Offer to generate the completion script automatically
    if click.confirm("\nWould you like to generate the completion script now?"):
        try:
            if shell == "fish":
                completion_dir = Path.home() / ".config" / "fish" / "completions"
                completion_dir.mkdir(parents=True, exist_ok=True)
                completion_file = completion_dir / "pdf-tools.fish"
            else:
                completion_file = Path.home() / f".pdf-tools-completion.{shell}"

            # Get the completion script using the correct method
            env = os.environ.copy()
            env["_PDF_TOOLS_COMPLETE"] = f"{shell}_source"

            completion_content = subprocess.check_output(["pdf-tools"], env=env, text=True, stderr=subprocess.DEVNULL)

            with open(completion_file, "w") as f:
                f.write(completion_content)

            click.echo(f"✅ Completion script generated: {completion_file}")

            if shell != "fish":
                profile_file = "~/.zshrc" if shell == "zsh" else "~/.bashrc"
                click.echo("\nDon't forget to run:")
                click.echo("")
                click.echo(f"  echo 'source {completion_file}' >> {profile_file}")
                click.echo(f"  source {profile_file}")
                click.echo("")

        except Exception as e:
            click.echo(f"❌ Failed to generate completion script: {e}")
            click.echo("\nPlease run manually:")
            click.echo(f"  {completion_script}")
            if shell != "fish":
                click.echo(f"  echo 'source {completion_file}' >> ~/.{shell}rc")


def main():
    cli()


if __name__ == "__main__":
    main()
