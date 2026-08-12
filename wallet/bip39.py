#!/usr/bin/env python3
"""BIP-39 mnemonic (seed phrase) generation and validation.

Pure standard library — no third-party dependencies, nothing leaves the machine.

This module creates *new* random seed phrases for wallets you control. It is not
and cannot be a recovery tool for a phrase you have lost: the smallest supported
phrase carries 128 bits of entropy, so searching for an existing wallet's phrase
is not a matter of having enough compute.

Reference: https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039.mediawiki
"""

from __future__ import annotations

import argparse
import hashlib
import secrets
import sys
import unicodedata
from pathlib import Path

WORDLIST_PATH = Path(__file__).resolve().parent / "english.txt"

# SHA-256 of the official BIP-39 English wordlist. Checked on every load: a
# single altered word would silently produce phrases no other wallet can read.
WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"

# word count -> entropy bits. Checksum is entropy_bits // 32, and
# (entropy_bits + checksum_bits) / 11 == word count.
STRENGTHS = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}

PBKDF2_ROUNDS = 2048
SEED_LEN = 64

_wordlist: list[str] | None = None
_word_index: dict[str, int] | None = None


def load_wordlist() -> list[str]:
    """Return the 2048-word English wordlist, verifying its integrity once."""
    global _wordlist, _word_index
    if _wordlist is None:
        raw = WORDLIST_PATH.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != WORDLIST_SHA256:
            raise ValueError(
                f"{WORDLIST_PATH} does not match the official BIP-39 English "
                f"wordlist (sha256 {digest}, expected {WORDLIST_SHA256})"
            )
        words = raw.decode("utf-8").split()
        if len(words) != 2048:
            raise ValueError(f"wordlist must hold 2048 words, found {len(words)}")
        _wordlist = words
        _word_index = {word: i for i, word in enumerate(words)}
    return _wordlist


def _index_of(word: str) -> int:
    load_wordlist()
    assert _word_index is not None
    try:
        return _word_index[word]
    except KeyError:
        raise ValueError(f"not a BIP-39 English word: {word!r}") from None


def entropy_to_mnemonic(entropy: bytes) -> str:
    """Encode raw entropy as a mnemonic, appending the BIP-39 checksum."""
    if len(entropy) not in (16, 20, 24, 28, 32):
        raise ValueError(
            f"entropy must be 16, 20, 24, 28 or 32 bytes, got {len(entropy)}"
        )
    words = load_wordlist()
    checksum_bits = len(entropy) * 8 // 32
    checksum = hashlib.sha256(entropy).digest()[0] >> (8 - checksum_bits)
    bits = (int.from_bytes(entropy, "big") << checksum_bits) | checksum

    count = (len(entropy) * 8 + checksum_bits) // 11
    return " ".join(
        words[(bits >> (11 * (count - 1 - i))) & 0x7FF] for i in range(count)
    )


def mnemonic_to_entropy(mnemonic: str) -> bytes:
    """Decode a mnemonic back to entropy, raising if the checksum is wrong."""
    words = normalize(mnemonic).split(" ")
    if len(words) not in STRENGTHS:
        raise ValueError(
            f"a mnemonic holds 12, 15, 18, 21 or 24 words, got {len(words)}"
        )

    bits = 0
    for word in words:
        bits = (bits << 11) | _index_of(word)

    entropy_bits = STRENGTHS[len(words)]
    checksum_bits = entropy_bits // 32
    checksum = bits & ((1 << checksum_bits) - 1)
    entropy = (bits >> checksum_bits).to_bytes(entropy_bits // 8, "big")

    expected = hashlib.sha256(entropy).digest()[0] >> (8 - checksum_bits)
    if checksum != expected:
        raise ValueError(
            "checksum mismatch — the phrase is mistyped, the words are in the "
            "wrong order, or it was not produced by BIP-39"
        )
    return entropy


def is_valid(mnemonic: str) -> bool:
    """True if the phrase is a well-formed BIP-39 mnemonic with a valid checksum."""
    try:
        mnemonic_to_entropy(mnemonic)
    except ValueError:
        return False
    return True


def generate(word_count: int = 24) -> str:
    """Generate a fresh mnemonic from the OS cryptographic RNG."""
    if word_count not in STRENGTHS:
        raise ValueError(
            f"word count must be one of {sorted(STRENGTHS)}, got {word_count}"
        )
    return entropy_to_mnemonic(secrets.token_bytes(STRENGTHS[word_count] // 8))


def normalize(mnemonic: str) -> str:
    """Canonical form: NFKD, lowercase, single-space separated.

    BIP-39 derives the seed from the exact bytes of the phrase, so a stray
    capital or double space changes every key it produces. Store and restore
    phrases in this form.
    """
    return " ".join(unicodedata.normalize("NFKD", mnemonic).lower().split())


def to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Stretch a mnemonic into the 64-byte BIP-32 seed.

    The passphrase (BIP-39 calls it the "25th word") selects a completely
    separate set of wallets. There is no way to tell a wrong passphrase from a
    right one — each yields a valid, empty wallet — so losing it loses the funds.
    """
    password = unicodedata.normalize("NFKD", " ".join(mnemonic.split()))
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac(
        "sha512", password.encode(), salt.encode(), PBKDF2_ROUNDS, SEED_LEN
    )


def _cmd_new(args: argparse.Namespace) -> int:
    for _ in range(args.count):
        print(generate(args.words))
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    phrase = " ".join(args.mnemonic) if args.mnemonic else sys.stdin.read()
    try:
        entropy = mnemonic_to_entropy(phrase)
    except ValueError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("VALID")
    print(f"words:      {len(normalize(phrase).split())}")
    print(f"entropy:    {len(entropy) * 8} bits")
    if args.show_entropy:
        print(f"entropy hex: {entropy.hex()}")
    print(f"canonical:  {normalize(phrase)}")
    return 0


def _cmd_seed(args: argparse.Namespace) -> int:
    phrase = " ".join(args.mnemonic) if args.mnemonic else sys.stdin.read()
    if not args.no_verify:
        mnemonic_to_entropy(phrase)
    print(to_seed(phrase, args.passphrase).hex())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bip39",
        description="Generate and validate BIP-39 seed phrases.",
        epilog="Generates new phrases only; it cannot recover an existing wallet.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="generate new seed phrases")
    new.add_argument(
        "-w", "--words", type=int, default=24, choices=sorted(STRENGTHS),
        help="words per phrase (default: 24)",
    )
    new.add_argument(
        "-n", "--count", type=int, default=1, help="how many phrases (default: 1)"
    )
    new.set_defaults(func=_cmd_new)

    check = sub.add_parser("check", help="validate a phrase's words and checksum")
    check.add_argument("mnemonic", nargs="*", help="the phrase (or pipe it on stdin)")
    check.add_argument(
        "--show-entropy", action="store_true", help="also print the raw entropy"
    )
    check.set_defaults(func=_cmd_check)

    seed = sub.add_parser("seed", help="derive the 64-byte BIP-32 seed")
    seed.add_argument("mnemonic", nargs="*", help="the phrase (or pipe it on stdin)")
    seed.add_argument("-p", "--passphrase", default="", help='BIP-39 "25th word"')
    seed.add_argument(
        "--no-verify", action="store_true",
        help="skip the checksum check (for phrases from non-BIP-39 wallets)",
    )
    seed.set_defaults(func=_cmd_seed)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
