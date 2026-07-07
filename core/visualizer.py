from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

from core.bit_utils import changed_bit_marker, format_byte, text_to_binary_lines


@dataclass
class ImageMetrics:
    mse: float
    psnr: float
    quality_percent: float


def create_difference_image(original: Image.Image, encoded: Image.Image) -> Image.Image:
    left = np.array(original.convert("RGB"), dtype=np.int16)
    right = np.array(encoded.convert("RGB"), dtype=np.int16)
    diff = np.abs(left - right) * 80
    diff = np.clip(diff, 0, 255).astype(np.uint8)
    return Image.fromarray(diff, "RGB")


def calculate_metrics(original: Image.Image, encoded: Image.Image) -> ImageMetrics:
    left = np.array(original.convert("RGB"), dtype=np.float32)
    right = np.array(encoded.convert("RGB"), dtype=np.float32)
    mse = float(np.mean((left - right) ** 2))
    if mse == 0:
        return ImageMetrics(0.0, float("inf"), 100.0)
    psnr = 20 * math.log10(255.0 / math.sqrt(mse))
    quality = max(0.0, min(100.0, 100.0 - (mse / 255.0 * 100.0)))
    return ImageMetrics(mse, psnr, quality)


def bit_plane_image(image: Image.Image, bit: int = 0) -> Image.Image:
    array = np.array(image.convert("L"), dtype=np.uint8)
    plane = ((array >> bit) & 1) * 255
    return Image.fromarray(plane.astype(np.uint8), "L").convert("RGB")


def sample_bit_changes(original: Image.Image, encoded: Image.Image, limit: int = 8) -> str:
    before = np.array(original.convert("RGB"), dtype=np.uint8).reshape(-1)
    after = np.array(encoded.convert("RGB"), dtype=np.uint8).reshape(-1)
    rows = []
    for index, (old, new) in enumerate(zip(before, after)):
        if old == new:
            continue
        pixel = index // 3
        channel = ["R", "G", "B"][index % 3]
        rows.append(
            f"Pixel {pixel:04d} {channel}\n"
            f"Original  {format_byte(int(old))}\n"
            f"Encoded   {format_byte(int(new))}\n"
            f"Changed   {changed_bit_marker(int(old), int(new))}"
        )
        if len(rows) >= limit:
            break
    return "\n\n".join(rows) if rows else "No bit changes detected yet."


def binary_message_preview(message: str, limit: int = 3200) -> str:
    binary = text_to_binary_lines(message)
    if len(binary) > limit:
        return binary[:limit] + "\n..."
    return binary


def inspect_pixel(original: Image.Image | None, encoded: Image.Image | None, x: int, y: int) -> str:
    if original is None:
        return "Load an original image first."
    original_rgb = original.convert("RGB")
    encoded_rgb = encoded.convert("RGB") if encoded else None
    if x < 0 or y < 0 or x >= original_rgb.width or y >= original_rgb.height:
        return "Pixel is outside the image."

    before = original_rgb.getpixel((x, y))
    after = encoded_rgb.getpixel((x, y)) if encoded_rgb else None
    lines = [f"Pixel ({x}, {y})"]
    for index, channel in enumerate(("R", "G", "B")):
        old = before[index]
        lines.append(f"{channel} original  {format_byte(old)}")
        if after:
            new = after[index]
            marker = " modified" if (old & 1) != (new & 1) else ""
            lines.append(f"{channel} encoded   {format_byte(new)}{marker}")
    return "\n".join(lines)
