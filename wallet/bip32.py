#!/usr/bin/env python3
"""BIP-32 hierarchical deterministic keys derived from a BIP-39 seed.

Pure standard library, including a small secp256k1 implementation — enough to
turn a seed phrase into the extended keys (xprv/xpub) a wallet is built from,
and to check that a phrase reproduces the accounts you expect.

The secp256k1 arithmetic here is straightforward and constant-*ish*, not
side-channel hardened. It is meant for generating and inspecting keys on a
machine you trust, not for signing on a shared or hostile host.

Reference: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

import bip39
import ripemd160

# secp256k1 domain parameters
P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

HARDENED = 0x80000000

VERSION_PRIVATE = 0x0488ADE4  # mainnet xprv
VERSION_PUBLIC = 0x0488B21E  # mainnet xpub

B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Optional[...] rather than `| None`: this is evaluated at import time, and the
# `|` form needs Python 3.10.
Point = Optional[Tuple[int, int]]


def _add(p: Point, q: Point) -> Point:
    """Add two points on secp256k1 (affine coordinates, None is infinity)."""
    if p is None:
        return q
    if q is None:
        return p
    px, py = p
    qx, qy = q
    if px == qx:
        if (py + qy) % P == 0:
            return None
        lam = (3 * px * px) * pow(2 * py, P - 2, P) % P
    else:
        lam = (qy - py) * pow(qx - px, P - 2, P) % P
    x = (lam * lam - px - qx) % P
    return x, (lam * (px - x) - py) % P


def _mul(k: int, p: Point = G) -> Point:
    """Scalar multiplication by double-and-add."""
    result: Point = None
    addend = p
    while k:
        if k & 1:
            result = _add(result, addend)
        addend = _add(addend, addend)
        k >>= 1
    return result


def compress(point: Point) -> bytes:
    """Serialize a public key point in 33-byte compressed form."""
    if point is None:
        raise ValueError("point at infinity has no serialization")
    x, y = point
    return (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big")


def private_to_public(private_key: bytes) -> bytes:
    return compress(_mul(int.from_bytes(private_key, "big")))


def hash160(data: bytes) -> bytes:
    return ripemd160.digest(hashlib.sha256(data).digest())


def b58check_encode(payload: bytes) -> str:
    data = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    number = int.from_bytes(data, "big")
    encoded = ""
    while number:
        number, rem = divmod(number, 58)
        encoded = B58_ALPHABET[rem] + encoded
    # Every leading zero byte is one leading '1' — this is what BIP-32 test
    # vectors 3 and 4 exist to catch.
    leading_zeros = len(data) - len(data.lstrip(b"\x00"))
    return "1" * leading_zeros + encoded


@dataclass(frozen=True)
class ExtendedKey:
    """A BIP-32 extended key: a key plus the chain code that extends it."""

    key: bytes  # 32-byte private key, or 33-byte compressed public key
    chain_code: bytes
    depth: int = 0
    parent_fingerprint: bytes = b"\x00\x00\x00\x00"
    child_number: int = 0
    private: bool = True

    @classmethod
    def from_seed(cls, seed: bytes) -> "ExtendedKey":
        """Derive the master key m from a BIP-39 seed."""
        if not 16 <= len(seed) <= 64:
            raise ValueError(f"seed must be 16-64 bytes, got {len(seed)}")
        digest = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        key, chain_code = digest[:32], digest[32:]
        if not 0 < int.from_bytes(key, "big") < N:
            raise ValueError("invalid master key for this seed; use another seed")
        return cls(key=key, chain_code=chain_code)

    def public_key(self) -> bytes:
        return private_to_public(self.key) if self.private else self.key

    def fingerprint(self) -> bytes:
        return hash160(self.public_key())[:4]

    def neutered(self) -> "ExtendedKey":
        """The matching public-only key — safe to hand out for watch-only use."""
        if not self.private:
            return self
        return ExtendedKey(
            key=self.public_key(),
            chain_code=self.chain_code,
            depth=self.depth,
            parent_fingerprint=self.parent_fingerprint,
            child_number=self.child_number,
            private=False,
        )

    def child(self, index: int) -> "ExtendedKey":
        """Derive one child key. Index >= 2**31 means hardened."""
        if not 0 <= index < 2**32:
            raise ValueError(f"child index out of range: {index}")
        if index >= HARDENED:
            if not self.private:
                raise ValueError(
                    "hardened derivation needs the private key; an xpub cannot "
                    f"derive index {index - HARDENED}'"
                )
            data = b"\x00" + self.key + index.to_bytes(4, "big")
        else:
            data = self.public_key() + index.to_bytes(4, "big")

        digest = hmac.new(self.chain_code, data, hashlib.sha512).digest()
        tweak = int.from_bytes(digest[:32], "big")
        if tweak >= N:
            raise ValueError(f"invalid child at index {index}; skip to the next")

        if self.private:
            child_key = (tweak + int.from_bytes(self.key, "big")) % N
            if child_key == 0:
                raise ValueError(f"invalid child at index {index}; skip to the next")
            key = child_key.to_bytes(32, "big")
        else:
            point = _add(_mul(tweak), _decompress(self.key))
            if point is None:
                raise ValueError(f"invalid child at index {index}; skip to the next")
            key = compress(point)

        return ExtendedKey(
            key=key,
            chain_code=digest[32:],
            depth=self.depth + 1,
            parent_fingerprint=self.fingerprint(),
            child_number=index,
            private=self.private,
        )

    def derive(self, path: str) -> "ExtendedKey":
        """Follow a derivation path such as m/44'/0'/0'/0/0."""
        key = self
        for element in parse_path(path):
            key = key.child(element)
        return key

    def serialize(self) -> str:
        version = VERSION_PRIVATE if self.private else VERSION_PUBLIC
        key_data = (b"\x00" + self.key) if self.private else self.key
        payload = (
            version.to_bytes(4, "big")
            + bytes([self.depth])
            + self.parent_fingerprint
            + self.child_number.to_bytes(4, "big")
            + self.chain_code
            + key_data
        )
        return b58check_encode(payload)


def _decompress(pubkey: bytes) -> Point:
    """Recover the full point from a 33-byte compressed public key."""
    if len(pubkey) != 33 or pubkey[0] not in (2, 3):
        raise ValueError("expected a 33-byte compressed public key")
    x = int.from_bytes(pubkey[1:], "big")
    y = pow((x * x * x + 7) % P, (P + 1) // 4, P)
    if pow(y, 2, P) != (x * x * x + 7) % P:
        raise ValueError("public key is not a point on secp256k1")
    if (y & 1) != (pubkey[0] & 1):
        y = P - y
    return x, y


def parse_path(path: str) -> list[int]:
    """Turn "m/44'/0'/0'/0/0" into a list of child indices."""
    cleaned = path.strip().rstrip("/")
    parts = cleaned.split("/")
    if parts and parts[0] in ("m", "M"):
        parts = parts[1:]
    elif cleaned:
        raise ValueError(f"derivation path must start at m: {path!r}")

    indices = []
    for part in parts:
        if not part:
            raise ValueError(f"empty element in derivation path {path!r}")
        hardened = part[-1] in ("'", "h", "H")
        number = part[:-1] if hardened else part
        if not number.isdigit():
            raise ValueError(f"bad element {part!r} in derivation path {path!r}")
        index = int(number)
        if index >= HARDENED:
            raise ValueError(f"index {index} out of range in path {path!r}")
        indices.append(index + HARDENED if hardened else index)
    return indices


def format_path(indices: list[int]) -> str:
    parts = ["m"]
    for index in indices:
        parts.append(
            f"{index - HARDENED}'" if index >= HARDENED else str(index)
        )
    return "/".join(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bip32",
        description="Derive BIP-32 extended keys from a seed phrase.",
    )
    parser.add_argument("mnemonic", nargs="*", help="the phrase (or pipe it on stdin)")
    parser.add_argument(
        "-d", "--path", default="m", help="derivation path (default: m, the master key)"
    )
    parser.add_argument("-p", "--passphrase", default="", help='BIP-39 "25th word"')
    parser.add_argument(
        "--public", action="store_true", help="print only the xpub, never the xprv"
    )
    args = parser.parse_args(argv)

    phrase = " ".join(args.mnemonic) if args.mnemonic else sys.stdin.read()
    try:
        bip39.mnemonic_to_entropy(phrase)
        seed = bip39.to_seed(phrase, args.passphrase)
        key = ExtendedKey.from_seed(seed).derive(args.path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"path:        {args.path}")
    print(f"fingerprint: {key.fingerprint().hex()}")
    print(f"xpub:        {key.neutered().serialize()}")
    if not args.public:
        # Both of these recover every key below this point — the seed recovers
        # the whole wallet. Withheld under --public so its output is shareable.
        print(f"seed:        {seed.hex()}")
        print(f"xprv:        {key.serialize()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
