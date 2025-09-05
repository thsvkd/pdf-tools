from pathlib import Path


def get_ext_files(root: str, ext: str) -> list[str]:
    """
    지정된 루트 디렉토리에서 특정 확장자의 파일들을 재귀적으로 찾음

    Args:
        root (str): 검색할 루트 디렉토리 경로
        ext (str): 찾을 파일 확장자 (예: '.pdf')

    Returns:
        list[str]: 찾은 파일 경로 리스트
    """
    return [str(p) for p in Path(root).rglob(f"*{ext}")]