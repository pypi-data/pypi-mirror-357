import importlib.resources
import shutil
import os

__all__ = ["export_files"]

FILES = ["3.txt", "4.txt", "5.txt"]

def export_files(destination: str = "."):
    """
    Экспортирует файлы 3.txt, 4.txt, 5.txt в указанную директорию (по умолчанию в текущую).
    """
    for filename in FILES:
        with importlib.resources.path(__package__, filename) as file_path:
            shutil.copy(file_path, os.path.join(destination, filename))
    print(f"Файлы {', '.join(FILES)} экспортированы в {os.path.abspath(destination)}")
