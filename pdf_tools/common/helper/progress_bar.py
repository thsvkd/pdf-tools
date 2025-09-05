from tqdm import tqdm


class ProgressBar:
    """
    A class to manage progress bars
    """

    def __init__(self, total: int, desc: str, unit: str, bar_format: str):
        self.pbar = tqdm(total=total, desc=desc, unit=unit, bar_format=bar_format)

    def update(self, n: int = 1):
        self.pbar.update(n)

    def close(self):
        self.pbar.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
