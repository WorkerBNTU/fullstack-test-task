from dataclasses import dataclass
from pathlib import Path

from src.core.config import Settings

_TEXT_READ_CHUNK_SIZE = 1 << 16  # 64 KiB
_PDF_PAGE_MARKER = b"/Type /Page"


@dataclass(frozen=True)
class ScanResult:
    scan_status: str
    scan_details: str
    requires_attention: bool


def scan_for_threats(
    *,
    original_name: str,
    size: int,
    mime_type: str,
    settings: Settings,
) -> ScanResult:
    """Same heuristics as before: suspicious extension, oversized file,
    mismatched pdf mime type. Pure function -- no I/O, easy to unit test."""
    reasons: list[str] = []
    extension = Path(original_name).suffix.lower()

    if extension in settings.suspicious_extensions:
        reasons.append(f"suspicious extension {extension}")

    if size > settings.max_file_size_bytes:
        reasons.append("file is larger than 10 MB")

    if extension == ".pdf" and mime_type not in {"application/pdf", "application/octet-stream"}:
        reasons.append("pdf extension does not match mime type")

    return ScanResult(
        scan_status="suspicious" if reasons else "clean",
        scan_details=", ".join(reasons) if reasons else "no threats found",
        requires_attention=bool(reasons),
    )


def _count_text_stats(path: Path) -> tuple[int, int]:
    """Line/char counts via streaming iteration instead of loading the whole
    file into one string with ``read_text`` -- avoids holding the entire
    file content in memory at once for large text files."""
    line_count = 0
    char_count = 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line_count += 1
            char_count += len(line)
    return line_count, char_count


def _count_pdf_pages_approx(path: Path, chunk_size: int = _TEXT_READ_CHUNK_SIZE) -> int:
    """Approximate PDF page count by scanning for a marker in fixed-size
    chunks, carrying over a small overlap so matches spanning a chunk
    boundary aren't missed. Avoids reading the whole (potentially large)
    PDF into memory as one bytes object."""
    overlap = b""
    count = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            window = overlap + chunk
            count += window.count(_PDF_PAGE_MARKER)
            overlap = window[-(len(_PDF_PAGE_MARKER) - 1):]
    return max(count, 1)


def extract_metadata(
    *,
    original_name: str,
    size: int,
    mime_type: str,
    stored_path: Path,
) -> dict:
    metadata: dict = {
        "extension": Path(original_name).suffix.lower(),
        "size_bytes": size,
        "mime_type": mime_type,
    }

    if mime_type.startswith("text/"):
        line_count, char_count = _count_text_stats(stored_path)
        metadata["line_count"] = line_count
        metadata["char_count"] = char_count
    elif mime_type == "application/pdf":
        metadata["approx_page_count"] = _count_pdf_pages_approx(stored_path)

    return metadata
