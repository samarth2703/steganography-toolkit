from __future__ import annotations

from pathlib import Path

SUPPORTED_FORMATS = {".png", ".bmp"}


def validate_image_path(path: str | Path) -> Path:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError("Image file was not found.")
    if image_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError("Only PNG and BMP images are supported.")
    return image_path


def capacity_bytes(width: int, height: int, channels: int = 3, lsb_count: int = 1) -> int:
    total_bits = width * height * channels * lsb_count
    return max((total_bits // 8) - 4, 0)


def human_size(size_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
