from pathlib import Path


def get_ext_files(root: str, ext: str) -> list[str]:
    """
    Recursively find files with a specific extension in the specified root directory

    Args:
        root (str): Root directory path to search
        ext (str): File extension to find (e.g., '.pdf')

    Returns:
        list[str]: List of found file paths
    """
    return [str(p) for p in Path(root).rglob(f"*{ext}")]
