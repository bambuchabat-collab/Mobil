#!/usr/bin/env python3
"""RIPEMD-160, used as a fallback when hashlib does not offer it.

BIP-32 needs RIPEMD-160 to compute key fingerprints, but OpenSSL 3 moved it to
the legacy provider, so `hashlib.new("ripemd160")` fails outright on a lot of
current systems. Rather than let key serialization break there, this module
implements it directly; `digest()` picks hashlib when it works and this when it
does not.

Reference: https://homes.esat.kuleuven.be/~bosselae/ripemd160.html
"""

from __future__ import annotations

import hashlib
import struct

# Message word order, left and right lines.
_R_LEFT = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
    3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
    1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
    4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13,
)
_R_RIGHT = (
    5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
    6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
    15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
    8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
    12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11,
)

# Rotation amounts, left and right lines.
_S_LEFT = (
    11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
    7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
    11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
    11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
    9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6,
)
_S_RIGHT = (
    8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
    9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
    9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
    15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
    8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11,
)

# Per-round constants, left and right lines.
_K_LEFT = (0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E)
_K_RIGHT = (0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000)

_INIT = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)

_MASK = 0xFFFFFFFF


def _f(round_index: int, x: int, y: int, z: int) -> int:
    if round_index == 0:
        return x ^ y ^ z
    if round_index == 1:
        return (x & y) | (~x & z)
    if round_index == 2:
        return (x | (~y & _MASK)) ^ z
    if round_index == 3:
        return (x & z) | (y & ~z)
    return x ^ (y | (~z & _MASK))


def _rol(value: int, count: int) -> int:
    value &= _MASK
    return ((value << count) | (value >> (32 - count))) & _MASK


def _compress(state: tuple[int, ...], block: bytes) -> tuple[int, ...]:
    words = struct.unpack("<16I", block)
    al, bl, cl, dl, el = state
    ar, br, cr, dr, er = state

    for j in range(80):
        rnd = j // 16

        temp = _rol(
            (al + _f(rnd, bl, cl, dl) + words[_R_LEFT[j]] + _K_LEFT[rnd]) & _MASK,
            _S_LEFT[j],
        )
        al, bl, cl, dl, el = el, (temp + el) & _MASK, bl, _rol(cl, 10), dl

        temp = _rol(
            (ar + _f(4 - rnd, br, cr, dr) + words[_R_RIGHT[j]] + _K_RIGHT[rnd])
            & _MASK,
            _S_RIGHT[j],
        )
        ar, br, cr, dr, er = er, (temp + er) & _MASK, br, _rol(cr, 10), dr

    return (
        (state[1] + cl + dr) & _MASK,
        (state[2] + dl + er) & _MASK,
        (state[3] + el + ar) & _MASK,
        (state[4] + al + br) & _MASK,
        (state[0] + bl + cr) & _MASK,
    )


def ripemd160(data: bytes) -> bytes:
    """Compute RIPEMD-160 in pure Python."""
    state = _INIT
    padded = (
        data
        + b"\x80"
        + b"\x00" * ((55 - len(data)) % 64)
        + struct.pack("<Q", (len(data) * 8) & 0xFFFFFFFFFFFFFFFF)
    )
    for offset in range(0, len(padded), 64):
        state = _compress(state, padded[offset : offset + 64])
    return struct.pack("<5I", *state)


def _hashlib_works() -> bool:
    try:
        hashlib.new("ripemd160", b"").digest()
    except (ValueError, TypeError):
        return False
    return True


_USE_HASHLIB = _hashlib_works()


def digest(data: bytes) -> bytes:
    """RIPEMD-160 via hashlib where available, otherwise the pure-Python code."""
    if _USE_HASHLIB:
        return hashlib.new("ripemd160", data).digest()
    return ripemd160(data)


if __name__ == "__main__":
    # Test vectors from the RIPEMD-160 specification.
    VECTORS = {
        "": "9c1185a5c5e9fc54612808977ee8f548b2258d31",
        "a": "0bdc9d2d256b3ee9daae347be6f4dc835a467ffe",
        "abc": "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc",
        "message digest": "5d0689ef49d2fae572b881b123a85ffa21595f36",
        "abcdefghijklmnopqrstuvwxyz": "f71c27109c692c1b56bbdceb5b9d2865b3708dbc",
        "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq": (
            "12a053384a9c0c88e405a06c27dcf49ada62eb2b"
        ),
    }
    failures = 0
    for message, expected in VECTORS.items():
        got = ripemd160(message.encode()).hex()
        ok = got == expected
        failures += not ok
        print(f"{message[:32]!r:40} {got} {'ok' if ok else f'FAIL != {expected}'}")
    print(f"hashlib available: {_USE_HASHLIB}")
    raise SystemExit(1 if failures else 0)
