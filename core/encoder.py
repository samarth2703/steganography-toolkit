from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

from core.bit_utils import bytes_to_bits
from core.crypto import encrypt_message
from core.validator import capacity_bytes

SENTINEL = b"STEG"


@dataclass
class EncodeResult:
    image: Image.Image
    payload_size: int
    changed_channels: int
    capacity: int
    encrypted: bool


def _payload_for_message(message: str, password: str = "") -> tuple[bytes, bool]:
    encrypted = bool(password)
    body = encrypt_message(message, password) if encrypted else message.encode("utf-8")
    flags = b"\x01" if encrypted else b"\x00"
    length = len(body).to_bytes(4, "big")
    return SENTINEL + flags + length + body, encrypted


def encode_image(image: Image.Image, message: str, password: str = "", lsb_count: int = 1) -> EncodeResult:
    if not message:
        raise ValueError("Enter a message before encoding.")
    if lsb_count not in (1, 2, 3):
        raise ValueError("LSB depth must be 1, 2, or 3.")

    rgb_image = image.convert("RGB")
    payload, encrypted = _payload_for_message(message, password)
    available = capacity_bytes(rgb_image.width, rgb_image.height, 3, lsb_count)
    if len(payload) > available:
        raise ValueError(f"Message is too large for this image. Capacity is {available} bytes.")

    bits = bytes_to_bits(payload)
    flat = np.array(rgb_image, dtype=np.uint8).reshape(-1)
    encoded = flat.copy()

    bit_index = 0
    mask = 0xFF ^ ((1 << lsb_count) - 1)
    for channel_index in range(len(encoded)):
        if bit_index >= len(bits):
            break
        chunk = bits[bit_index : bit_index + lsb_count].ljust(lsb_count, "0")
        encoded[channel_index] = (int(encoded[channel_index]) & mask) | int(chunk, 2)
        bit_index += lsb_count

    changed = int(np.count_nonzero(flat != encoded))
    array = encoded.reshape((rgb_image.height, rgb_image.width, 3))
    return EncodeResult(
        image=Image.fromarray(array, "RGB"),
        payload_size=len(payload),
        changed_channels=changed,
        capacity=available,
        encrypted=encrypted,
    )
