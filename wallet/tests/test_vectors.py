#!/usr/bin/env python3
"""Checks bip39.py and bip32.py against the official BIP-39 and BIP-32 vectors.

Run with: python3 wallet/tests/test_vectors.py   (or: python3 -m pytest)

bip39_vectors.json holds the English vectors from trezor/python-mnemonic; they
all use the passphrase "TREZOR". bip32_vectors.json holds test vectors 1-4 from
the BIP-32 specification, including the leading-zero cases that catch a broken
base58 encoder.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bip32
import bip39
import ripemd160

VECTORS = Path(__file__).resolve().parent
BIP39_VECTORS = json.loads((VECTORS / "bip39_vectors.json").read_text())
BIP32_VECTORS = json.loads((VECTORS / "bip32_vectors.json").read_text())
TREZOR_PASSPHRASE = "TREZOR"


class TestWordlist(unittest.TestCase):
    def test_integrity(self):
        words = bip39.load_wordlist()
        self.assertEqual(len(words), 2048)
        self.assertEqual(words[0], "abandon")
        self.assertEqual(words[-1], "zoo")

    def test_sorted_and_unique(self):
        # BIP-39 requires the list be sorted, and the first four letters of
        # every word to be unique — that is what makes 4-letter entry work.
        words = bip39.load_wordlist()
        self.assertEqual(words, sorted(words))
        self.assertEqual(len({w[:4] for w in words}), 2048)


class TestBip39Vectors(unittest.TestCase):
    def test_entropy_to_mnemonic(self):
        for vector in BIP39_VECTORS:
            with self.subTest(entropy=vector["entropy"]):
                got = bip39.entropy_to_mnemonic(bytes.fromhex(vector["entropy"]))
                self.assertEqual(got, vector["mnemonic"])

    def test_mnemonic_to_entropy(self):
        for vector in BIP39_VECTORS:
            with self.subTest(mnemonic=vector["mnemonic"][:32]):
                got = bip39.mnemonic_to_entropy(vector["mnemonic"])
                self.assertEqual(got.hex(), vector["entropy"])

    def test_to_seed(self):
        for vector in BIP39_VECTORS:
            with self.subTest(mnemonic=vector["mnemonic"][:32]):
                got = bip39.to_seed(vector["mnemonic"], TREZOR_PASSPHRASE)
                self.assertEqual(got.hex(), vector["seed"])

    def test_master_key(self):
        for vector in BIP39_VECTORS:
            with self.subTest(mnemonic=vector["mnemonic"][:32]):
                seed = bip39.to_seed(vector["mnemonic"], TREZOR_PASSPHRASE)
                master = bip32.ExtendedKey.from_seed(seed)
                self.assertEqual(master.serialize(), vector["xprv"])


class TestBip39Properties(unittest.TestCase):
    def test_generate_round_trips(self):
        for words in sorted(bip39.STRENGTHS):
            with self.subTest(words=words):
                mnemonic = bip39.generate(words)
                self.assertEqual(len(mnemonic.split()), words)
                self.assertTrue(bip39.is_valid(mnemonic))
                entropy = bip39.mnemonic_to_entropy(mnemonic)
                self.assertEqual(len(entropy) * 8, bip39.STRENGTHS[words])
                self.assertEqual(bip39.entropy_to_mnemonic(entropy), mnemonic)

    def test_generated_phrases_are_distinct(self):
        # A repeat here would mean the RNG is broken; with 128 bits of entropy
        # the odds of a genuine collision are nil.
        phrases = {bip39.generate(12) for _ in range(64)}
        self.assertEqual(len(phrases), 64)

    def test_rejects_bad_checksum(self):
        # Same words, last one swapped for another valid word.
        broken = "abandon " * 11 + "abandon"
        self.assertFalse(bip39.is_valid(broken))
        with self.assertRaises(ValueError):
            bip39.mnemonic_to_entropy(broken)

    def test_rejects_unknown_word(self):
        vector = BIP39_VECTORS[0]["mnemonic"].split()
        vector[3] = "kolobok"
        self.assertFalse(bip39.is_valid(" ".join(vector)))

    def test_rejects_wrong_word_count(self):
        for count in (0, 11, 13, 23, 25):
            with self.subTest(count=count):
                self.assertFalse(bip39.is_valid(" ".join(["abandon"] * count)))

    def test_rejects_reordered_words(self):
        words = BIP39_VECTORS[2]["mnemonic"].split()
        words[0], words[1] = words[1], words[0]
        self.assertFalse(bip39.is_valid(" ".join(words)))

    def test_rejects_bad_entropy_length(self):
        for length in (0, 15, 17, 33):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    bip39.entropy_to_mnemonic(b"\x00" * length)

    def test_generate_rejects_bad_word_count(self):
        for count in (0, 11, 16, 25):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    bip39.generate(count)

    def test_normalization(self):
        canonical = BIP39_VECTORS[0]["mnemonic"]
        messy = f"  {canonical.upper().replace(' ', '   ')}\n"
        self.assertEqual(bip39.normalize(messy), canonical)
        self.assertTrue(bip39.is_valid(messy))
        # Whitespace is normalized before hashing, so the seed is unchanged...
        self.assertEqual(
            bip39.to_seed(f"  {canonical}  ".replace(" ", "  ")),
            bip39.to_seed(canonical),
        )
        # ...but case is not: it produces a different, equally valid wallet.
        self.assertNotEqual(
            bip39.to_seed(canonical.upper()), bip39.to_seed(canonical)
        )

    def test_passphrase_changes_seed(self):
        mnemonic = BIP39_VECTORS[0]["mnemonic"]
        self.assertNotEqual(
            bip39.to_seed(mnemonic), bip39.to_seed(mnemonic, "hunter2")
        )
        self.assertEqual(len(bip39.to_seed(mnemonic, "hunter2")), 64)


class TestBip32Vectors(unittest.TestCase):
    def test_derivation_chains(self):
        for vector in BIP32_VECTORS:
            master = bip32.ExtendedKey.from_seed(bytes.fromhex(vector["seed"]))
            for chain in vector["chains"]:
                with self.subTest(vector=vector["vector"], path=chain["path"]):
                    key = master.derive(chain["path"])
                    self.assertEqual(key.serialize(), chain["xprv"])
                    self.assertEqual(key.neutered().serialize(), chain["xpub"])

    def test_public_derivation_matches_private(self):
        """An xpub derives the same non-hardened children as its xprv."""
        master = bip32.ExtendedKey.from_seed(bytes.fromhex(BIP32_VECTORS[0]["seed"]))
        account = master.derive("m/44'/0'/0'")
        watch_only = account.neutered()
        for index in (0, 1, 7, 1000):
            with self.subTest(index=index):
                self.assertEqual(
                    account.child(index).neutered().serialize(),
                    watch_only.child(index).serialize(),
                )

    def test_xpub_cannot_derive_hardened(self):
        master = bip32.ExtendedKey.from_seed(bytes.fromhex(BIP32_VECTORS[0]["seed"]))
        with self.assertRaises(ValueError):
            master.neutered().child(bip32.HARDENED)


class TestBip32Internals(unittest.TestCase):
    def test_parse_path(self):
        self.assertEqual(bip32.parse_path("m"), [])
        self.assertEqual(bip32.parse_path("m/0"), [0])
        self.assertEqual(bip32.parse_path("m/0'"), [bip32.HARDENED])
        self.assertEqual(bip32.parse_path("m/0h"), [bip32.HARDENED])
        self.assertEqual(bip32.parse_path("m/0H"), [bip32.HARDENED])
        self.assertEqual(bip32.parse_path("m/44'/60'/0'/0/0")[0], 44 + bip32.HARDENED)
        self.assertEqual(bip32.parse_path(" m/1/2/ "), [1, 2])

    def test_parse_path_rejects_garbage(self):
        for path in ("44'/0'", "m//0", "m/x", "m/-1", "m/2147483648", "m/0''"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    bip32.parse_path(path)

    def test_format_path_round_trip(self):
        for path in ("m", "m/0", "m/44'/60'/0'/0/0", "m/0'/1/2'/2/1000000000"):
            with self.subTest(path=path):
                self.assertEqual(bip32.format_path(bip32.parse_path(path)), path)

    def test_point_arithmetic(self):
        self.assertIsNone(bip32._mul(0))
        self.assertIsNone(bip32._mul(bip32.N))
        self.assertEqual(bip32._mul(1), bip32.G)
        self.assertEqual(bip32._add(bip32.G, None), bip32.G)
        # 2G + G == 3G, via two different routes
        self.assertEqual(
            bip32._add(bip32._add(bip32.G, bip32.G), bip32.G), bip32._mul(3)
        )
        # k*G and (N-k)*G differ only in the sign of y
        x1, y1 = bip32._mul(7)
        x2, y2 = bip32._mul(bip32.N - 7)
        self.assertEqual(x1, x2)
        self.assertEqual(y1, bip32.P - y2)

    def test_point_on_curve(self):
        for k in (1, 2, 3, 12345, bip32.N - 1):
            with self.subTest(k=k):
                x, y = bip32._mul(k)
                self.assertEqual(pow(y, 2, bip32.P), (pow(x, 3, bip32.P) + 7) % bip32.P)

    def test_compress_round_trip(self):
        for k in (1, 2, 3, 12345, bip32.N - 1):
            with self.subTest(k=k):
                point = bip32._mul(k)
                self.assertEqual(bip32._decompress(bip32.compress(point)), point)

    def test_decompress_rejects_off_curve(self):
        # x = 5 has no y on secp256k1 (x = 1 does, so it is a poor test case).
        with self.assertRaises(ValueError):
            bip32._decompress(b"\x02" + (5).to_bytes(32, "big"))
        with self.assertRaises(ValueError):
            bip32._decompress(b"\x04" + b"\x01" * 32)  # uncompressed prefix
        with self.assertRaises(ValueError):
            bip32._decompress(b"\x02" + b"\x01" * 31)  # too short

    def test_base58check_leading_zeros(self):
        # One '1' per leading zero byte — BIP-32 vectors 3 and 4 depend on it.
        self.assertEqual(bip32.b58check_encode(b"\x00"), "1Wh4bh")
        self.assertTrue(bip32.b58check_encode(b"\x00\x00\x01").startswith("11"))

    def test_hash160(self):
        # RIPEMD160(SHA256(b"")) — a fixed, widely published value.
        self.assertEqual(
            bip32.hash160(b"").hex(), "b472a266d0bd89c13706a4132ccfb16f7c3b9fcb"
        )

    def test_from_seed_rejects_bad_length(self):
        for length in (0, 15, 65):
            with self.subTest(length=length):
                with self.assertRaises(ValueError):
                    bip32.ExtendedKey.from_seed(b"\x00" * length)


class TestRipemd160(unittest.TestCase):
    """The pure-Python fallback used where OpenSSL 3 hides RIPEMD-160."""

    SPEC_VECTORS = {
        b"": "9c1185a5c5e9fc54612808977ee8f548b2258d31",
        b"a": "0bdc9d2d256b3ee9daae347be6f4dc835a467ffe",
        b"abc": "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc",
        b"message digest": "5d0689ef49d2fae572b881b123a85ffa21595f36",
        b"abcdefghijklmnopqrstuvwxyz": "f71c27109c692c1b56bbdceb5b9d2865b3708dbc",
        b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq": (
            "12a053384a9c0c88e405a06c27dcf49ada62eb2b"
        ),
    }

    def test_spec_vectors(self):
        for message, expected in self.SPEC_VECTORS.items():
            with self.subTest(message=message[:24]):
                self.assertEqual(ripemd160.ripemd160(message).hex(), expected)

    def test_padding_boundaries(self):
        """Lengths either side of every block and length-field boundary."""
        for length in (54, 55, 56, 57, 63, 64, 65, 119, 120, 128):
            with self.subTest(length=length):
                data = bytes(range(256))[:1] * length
                self.assertEqual(len(ripemd160.ripemd160(data)), 20)
        # Cross-check against hashlib wherever it is actually available.
        if ripemd160._USE_HASHLIB:
            import hashlib as _hashlib

            for length in range(0, 130):
                with self.subTest(length=length):
                    data = bytes((i * 7 + 3) % 256 for i in range(length))
                    self.assertEqual(
                        ripemd160.ripemd160(data),
                        _hashlib.new("ripemd160", data).digest(),
                    )

    def test_bip32_vectors_with_fallback_forced(self):
        """The official BIP-32 chains still pass on the pure-Python path."""
        original = ripemd160._USE_HASHLIB
        ripemd160._USE_HASHLIB = False
        try:
            for vector in BIP32_VECTORS:
                master = bip32.ExtendedKey.from_seed(bytes.fromhex(vector["seed"]))
                for chain in vector["chains"]:
                    with self.subTest(vector=vector["vector"], path=chain["path"]):
                        key = master.derive(chain["path"])
                        self.assertEqual(key.serialize(), chain["xprv"])
                        self.assertEqual(key.neutered().serialize(), chain["xpub"])
        finally:
            ripemd160._USE_HASHLIB = original


class TestEndToEnd(unittest.TestCase):
    def test_phrase_to_account(self):
        """A generated phrase derives stable, valid keys."""
        mnemonic = bip39.generate(24)
        seed = bip39.to_seed(mnemonic)
        first = bip32.ExtendedKey.from_seed(seed).derive("m/44'/0'/0'/0/0")
        second = bip32.ExtendedKey.from_seed(
            bip39.to_seed(mnemonic)
        ).derive("m/44'/0'/0'/0/0")

        self.assertEqual(first.serialize(), second.serialize())
        self.assertTrue(first.serialize().startswith("xprv"))
        self.assertTrue(first.neutered().serialize().startswith("xpub"))
        self.assertEqual(first.depth, 5)
        self.assertEqual(len(first.key), 32)
        self.assertEqual(len(first.chain_code), 32)

    def test_passphrase_yields_a_different_wallet(self):
        mnemonic = BIP39_VECTORS[0]["mnemonic"]
        plain = bip32.ExtendedKey.from_seed(bip39.to_seed(mnemonic))
        with_passphrase = bip32.ExtendedKey.from_seed(
            bip39.to_seed(mnemonic, "hunter2")
        )
        self.assertNotEqual(plain.serialize(), with_passphrase.serialize())


if __name__ == "__main__":
    unittest.main(verbosity=2)
