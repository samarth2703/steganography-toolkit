from __future__ import annotations

import base64
import hashlib


class CryptoUnavailableError(RuntimeError):
    pass


def _get_fernet():
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:
        raise CryptoUnavailableError(
            "Install the cryptography package to use password protection."
        ) from exc
    return Fernet, InvalidToken


def derive_key(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_message(message: str, password: str) -> bytes:
    Fernet, _ = _get_fernet()
    return Fernet(derive_key(password)).encrypt(message.encode("utf-8"))


def decrypt_message(token: bytes, password: str) -> str:
    Fernet, InvalidToken = _get_fernet()
    try:
        data = Fernet(derive_key(password)).decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Incorrect password or corrupted hidden message.") from exc
    return data.decode("utf-8")
