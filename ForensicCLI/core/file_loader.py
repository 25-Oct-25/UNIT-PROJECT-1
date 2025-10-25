"""
core/file_loader.py

وظيفة هذا الملف:
- قراءة الملفات من مجلد معين
- فلترة الملفات حسب امتدادات مدعومة
- دعم مسح مجلدات بشكل recursive أو non-recursive
- إرجاع قائمة من pathlib.Path للملفات الجاهزة للتحليل
"""

from pathlib import Path
from typing import List, Optional, Iterable
import mimetypes
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


SUPPORTED_EXTS = {".txt", ".pdf", ".jpg", ".jpeg", ".png"}


class NoFilesFoundError(Exception):
    """Raised when no supported files are found in the given path."""


def is_supported_file(path: Path, supported_exts: Optional[Iterable[str]] = None) -> bool:
    """Return True if path is a file and has a supported extension."""
    exts = set(supported_exts) if supported_exts else SUPPORTED_EXTS
    if not path.is_file():
        return False
    return path.suffix.lower() in exts


def load_files_from_directory(
    dir_path: str,
    recursive: bool = True,
    supported_exts: Optional[Iterable[str]] = None
) -> List[Path]:
    """
    Scan the given directory and return a list of files that match supported_exts.

    Args:
        dir_path: path to folder (string)
        recursive: whether to scan subfolders (default True)
        supported_exts: optional iterable of extensions (e.g. ['.txt','.pdf'])

    Returns:
        List[pathlib.Path] of matched files

    Raises:
        FileNotFoundError: if the provided dir_path does not exist or is not a directory
        NoFilesFoundError: if no files matching supported_exts are found
    """
    p = Path(dir_path)

    if not p.exists():
        logger.error("The provided path does not exist: %s", dir_path)
        raise FileNotFoundError(f"Path not found: {dir_path}")

    if not p.is_dir():
        logger.error("The provided path is not a directory: %s", dir_path)
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    exts = set(ext.lower() for ext in supported_exts) if supported_exts else SUPPORTED_EXTS

    files: List[Path] = []
    if recursive:
        for fp in p.rglob("*"):
            if is_supported_file(fp, exts):
                files.append(fp)
    else:
        for fp in p.iterdir():
            if is_supported_file(fp, exts):
                files.append(fp)

    if not files:
        logger.warning("No supported files found in: %s", dir_path)
        raise NoFilesFoundError(f"No supported files found in: {dir_path}")

    # Optional: sort files by name or modification time
    files.sort()  # alphabetical; change if you prefer other sorting
    logger.info("Found %d supported files in %s", len(files), dir_path)
    return files


def guess_mime_type(file_path: Path) -> Optional[str]:
    """
    Try to guess the MIME type of a file using mimetypes.
    Note: mimetypes is extension-based, not content-based.
    """
    mime, _ = mimetypes.guess_type(str(file_path))
    return mime
