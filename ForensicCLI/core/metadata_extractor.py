import os
import mimetypes
import exifread
from PyPDF2 import PdfReader
from datetime import datetime

def extract_metadata(file_path):
    """
    Extract metadata and general file information.
    Works for images, PDFs, and text files.
    """
    metadata = {}
    try:
        # Basic file info
        metadata["file_name"] = os.path.basename(file_path)
        metadata["file_size_kb"] = round(os.path.getsize(file_path) / 1024, 2)
        metadata["file_type"] = mimetypes.guess_type(file_path)[0] or "Unknown"
        metadata["last_modified"] = datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Image metadata
        if metadata["file_type"] and "image" in metadata["file_type"]:
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
                metadata["exif_data"] = {tag: str(tags[tag]) for tag in tags}

        # PDF metadata
        elif metadata["file_type"] == "application/pdf":
            reader = PdfReader(file_path)
            info = reader.metadata
            metadata["pdf_metadata"] = {key: str(info[key]) for key in info.keys() if info[key]}
            metadata["pages"] = len(reader.pages)

        # Text file metadata (basic)
        elif metadata["file_type"] and "text" in metadata["file_type"]:
            with open(file_path, "r", errors="ignore") as f:
                content = f.read()
                metadata["line_count"] = len(content.splitlines())
                metadata["word_count"] = len(content.split())

    except Exception as e:
        metadata["error"] = str(e)

    return metadata
