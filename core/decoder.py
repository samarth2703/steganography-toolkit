from __future__ import annotations

import numpy as np
from PIL import Image

from core.bit_utils import bits_to_bytes
from core.crypto import decrypt_message
from core.encoder import SENTINEL


def _read_bytes(flat: np.ndarray, byte_count: int, lsb_count: int) -> bytes:
    needed_bits = byte_count * 8
    bits: list[str] = []
    mask = (1 << lsb_count) - 1
    for value in flat:
        bits.append(f"{int(value) & mask:0{lsb_count}b}")
        if sum(len(part) for part in bits) >= needed_bits:
            break
    return bits_to_bytes("".join(bits)[:needed_bits])


def decode_image(image: Image.Image, password: str = "", lsb_count: int = 1) -> tuple[str, bool]:
    if lsb_count not in (1, 2, 3):
        raise ValueError("LSB depth must be 1, 2, or 3.")

    rgb_image = image.convert("RGB")
    flat = np.array(rgb_image, dtype=np.uint8).reshape(-1)
    header = _read_bytes(flat, 9, lsb_count)
    if len(header) < 9 or header[:4] != SENTINEL:
        raise ValueError("No compatible hidden message was found in this image.")

    encrypted = header[4] == 1
    message_length = int.from_bytes(header[5:9], "big")
    payload = _read_bytes(flat, 9 + message_length, lsb_count)[9:]

    if encrypted:
        if not password:
            return payload.decode("utf-8", errors="replace"), True
        return decrypt_message(payload, password), True
    return payload.decode("utf-8", errors="replace"), False
