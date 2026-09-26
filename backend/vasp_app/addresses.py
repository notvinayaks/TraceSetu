"""Mainnet address syntax/checksums; an address does not establish its owner."""

import hashlib
import re
from eth_utils import is_checksum_address

BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BECH32 = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def decode58(value):
    n = 0
    for char in value:
        if char not in BASE58:
            raise ValueError("Invalid Base58 character")
        n = n * 58 + BASE58.index(char)
    return b"\0" * (len(value) - len(value.lstrip("1"))) + n.to_bytes((n.bit_length() + 7) // 8, "big")


def encode58(data):
    n, result = int.from_bytes(data, "big"), ""
    while n:
        n, r = divmod(n, 58)
        result = BASE58[r] + result
    return "1" * (len(data) - len(data.lstrip(b"\0"))) + result


def tron_from_hex(value):
    data = bytes.fromhex(value)
    return encode58(data + hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4])


def validate_address(chain, address):
    address = address.strip()
    if chain in ("ethereum", "bnb", "polygon"):
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", address):
            raise ValueError("Expected a 20-byte EVM address")
        body = address[2:]
        if body != body.lower() and body != body.upper() and not is_checksum_address(address):
            raise ValueError("Invalid EIP-55 checksum")
        return address.lower()
    if chain == "solana":
        if len(address) > 44 or len(decode58(address)) != 32:
            raise ValueError("Expected a 32-byte Solana public key")
        return address
    if chain in ("bitcoin", "tron") and not address.lower().startswith("bc1"):
        data = decode58(address)
        if len(data) != 25 or hashlib.sha256(hashlib.sha256(data[:-4]).digest()).digest()[:4] != data[-4:]:
            raise ValueError("Invalid Base58Check address")
        if data[0] not in ([0, 5] if chain == "bitcoin" else [65]):
            raise ValueError("Address is not on the selected mainnet")
        return address
    if chain == "bitcoin":
        if address != address.lower() and address != address.upper():
            raise ValueError("Mixed-case SegWit address")
        a = address.lower()
        if len(a) > 90 or not a.startswith("bc1") or any(c not in BECH32 for c in a[3:]):
            raise ValueError("Invalid SegWit address")
        data = [BECH32.index(c) for c in a[3:]]
        chk = 1
        for v in [3, 3, 0, 2, 3] + data:
            top = chk >> 25
            chk = (chk & 0x1FFFFFF) << 5 ^ v
            for i, g in enumerate([0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]):
                if (top >> i) & 1:
                    chk ^= g
        if len(data) < 7 or data[0] > 16 or chk != (1 if data[0] == 0 else 0x2BC830A3):
            raise ValueError("Invalid Bech32/Bech32m checksum")
        bits = 0
        acc = 0
        decoded = []
        for v in data[1:-6]:
            acc = (acc << 5) | v
            bits += 5
            while bits >= 8:
                bits -= 8
                decoded.append((acc >> bits) & 255)
        if bits >= 5 or ((acc << (8 - bits)) & 255):
            raise ValueError("Invalid SegWit padding")
        if not 2 <= len(decoded) <= 40 or (data[0] == 0 and len(decoded) not in (20, 32)):
            raise ValueError("Invalid witness program")
        return a
    raise ValueError("Unsupported chain")
