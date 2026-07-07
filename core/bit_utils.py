from __future__ import annotations


def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in data)


def bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8:
        bits = bits[: len(bits) - (len(bits) % 8)]
    return bytes(int(bits[index : index + 8], 2) for index in range(0, len(bits), 8))


def text_to_binary_lines(text: str) -> str:
    data = text.encode("utf-8", errors="replace")
    return "\n".join(f"{byte:08b}" for byte in data)


def format_byte(value: int) -> str:
    return f"{value:08b}"


def changed_bit_marker(before: int, after: int) -> str:
    return "       ^" if (before & 1) != (after & 1) else "        "
