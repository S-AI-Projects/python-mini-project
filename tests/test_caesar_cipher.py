"""
Tests for utilities/Caesar-Cipher/Caesar-Cipher.py

Focus areas:
- Regression test for "Playfair cipher decryption skips the last character
  pair" (issue #1823): every pair in the processed message - including the
  final one - must be encrypted/decrypted, even when the filtered message
  has an odd number of letters.
- Round-trip sanity checks for the other ciphers in the suite.

The module file uses hyphens in its name, so it's loaded via importlib
rather than a normal `import` statement.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Caesar-Cipher"
    / "Caesar-Cipher.py"
)


@pytest.fixture
def cipher_suite():
    spec = importlib.util.spec_from_file_location("cipher_suite", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cipher_suite"] = module
    spec.loader.exec_module(module)
    return module


# ── Caesar cipher ────────────────────────────────────────────────────────────

def test_caesar_round_trip(cipher_suite):
    plaintext = "Hello, World!"
    enc = cipher_suite.caesar_cipher(plaintext, 5, "E")
    dec = cipher_suite.caesar_cipher(enc, 5, "D")
    assert dec == plaintext


def test_caesar_standard_shift_abc(cipher_suite):
    """Cover the 'abc' shifted by 3 fixture in both encrypt and decrypt modes."""
    enc = cipher_suite.caesar_cipher("abc", 3, "E")
    assert enc == "def"
    dec = cipher_suite.caesar_cipher("def", 3, "D")
    assert dec == "abc"


def test_caesar_zero_and_full_alphabet_shift(cipher_suite):
    """Cover zero shift and full-alphabet cycle shifts (26 and -26)."""
    assert cipher_suite.caesar_cipher("abc", 0, "E") == "abc"
    assert cipher_suite.caesar_cipher("abc", 26, "E") == "abc"
    assert cipher_suite.caesar_cipher("abc", -26, "E") == "abc"


def test_caesar_preserves_punctuation_casing_and_unicode(cipher_suite):
    """Verify casing is preserved and non-alphabetic/Unicode characters are untouched."""
    assert cipher_suite.caesar_cipher("AbC", 3, "E") == "DeF"
    assert cipher_suite.caesar_cipher("Hello, World! 123", 3, "E") == "Khoor, Zruog! 123"
    assert cipher_suite.caesar_cipher("café", 3, "E") == "fdié"


def test_caesar_empty_message_and_rejection_branches(cipher_suite):
    """Verify empty input returns empty string and non-alpha characters pass through."""
    assert cipher_suite.caesar_cipher("", 3, "E") == ""
    assert cipher_suite.caesar_cipher("", 3, "D") == ""
    assert cipher_suite.caesar_cipher("!", 3, "E") == "!"
    assert cipher_suite.caesar_cipher("123 !?@#", 3, "E") == "123 !?@#"


def test_caesar_caller_input_integrity_and_subsequent_valid_call(cipher_suite):
    """
    Verify caller input string is preserved, empty message call succeeds,
    subsequent ordinary valid call succeeds, and original string remains intact.
    """
    original = "abc"
    res_empty = cipher_suite.caesar_cipher("", 3, "E")
    assert res_empty == ""

    res_valid = cipher_suite.caesar_cipher(original, 3, "E")
    assert res_valid == "def"
    assert original == "abc"


# ── Vigenere cipher ───────────────────────────────────────────────────────────

def test_vigenere_round_trip(cipher_suite):
    plaintext = "Attack at dawn"
    enc = cipher_suite.vigenere_cipher(plaintext, "LEMON", "E")
    dec = cipher_suite.vigenere_cipher(enc, "LEMON", "D")
    assert dec == plaintext


# ── Atbash cipher ─────────────────────────────────────────────────────────────

def test_atbash_is_its_own_inverse(cipher_suite):
    plaintext = "Secret Message"
    enc = cipher_suite.atbash_cipher(plaintext)
    dec = cipher_suite.atbash_cipher(enc)
    assert dec == plaintext


# ── Playfair cipher ───────────────────────────────────────────────────────────

def test_playfair_round_trip_even_length(cipher_suite):
    """Baseline: a message whose filtered length is already even should
    round-trip cleanly (this case worked even before the fix)."""
    keyword = "MONARCHY"
    plaintext = "HELLO WORLD"
    enc = cipher_suite.playfair_cipher(plaintext, keyword, "E")
    dec = cipher_suite.playfair_cipher(enc, keyword, "D")
    # Encryption always produces an even-length ciphertext.
    assert len(enc) % 2 == 0
    # Decryption must recover every character the encryption produced,
    # including the final digraph.
    assert len(dec) == len(enc)
    assert dec == "HELXLOWORLDX"  # X-padded plaintext playfair actually encoded


def test_playfair_decrypt_odd_length_processes_final_letter(cipher_suite):
    """
    Regression test for issue #1823.

    When the filtered ciphertext has an ODD number of letters (e.g. a
    corrupted or hand-typed message), the trailing, unpaired letter must
    still be run through a full digraph instead of being silently dropped
    by the loop.
    """
    keyword = "MONARCHY"
    ciphertext = "ABCDE"  # 5 letters -> odd length
    dec = cipher_suite.playfair_cipher(ciphertext, keyword, "D")
    # Before the fix, the trailing "E" was dropped entirely and only 4
    # characters came back out. After the fix, the letter is padded with
    # "X" to complete its digraph, so all 6 processed characters are
    # decrypted.
    assert len(dec) == 6


def test_playfair_encrypt_decrypt_roundtrip_various_lengths(cipher_suite):
    """Encrypt/decrypt round trip should preserve every character produced
    during encryption for messages of several different lengths, including
    ones that require internal X-padding for repeated letters."""
    keyword = "PLAYFAIREXAMPLE"
    for plaintext in ["A", "AB", "ABC", "BALLOON", "MISSISSIPPI", "X"]:
        enc = cipher_suite.playfair_cipher(plaintext, keyword, "E")
        dec = cipher_suite.playfair_cipher(enc, keyword, "D")
        assert len(dec) == len(enc), f"Lost characters decrypting {plaintext!r}"


def test_playfair_matrix_has_25_unique_letters(cipher_suite):
    matrix = cipher_suite.generate_playfair_matrix("MONARCHY")
    letters = [c for row in matrix for c in row]
    assert len(letters) == 25
    assert len(set(letters)) == 25
    assert "J" not in letters


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))