"""Translate English text to Pig Latin."""

import re


_ASCII_WORD = re.compile(r"[A-Za-z]+")
_VOWELS = "aeiou"


def _translate_letters(letters: str) -> str:
    """Translate a lowercase sequence of ASCII letters."""
    word = letters.lower()

    if word[0] in _VOWELS:
        translated = f"{word}way"
    else:
        cluster_end = 0
        while cluster_end < len(word):
            letter = word[cluster_end]
            is_vowel = letter in _VOWELS or (letter == "y" and cluster_end > 0)
            is_qu_u = letter == "u" and cluster_end > 0 and word[cluster_end - 1] == "q"
            if is_vowel and not is_qu_u:
                break
            cluster_end += 1

        translated = f"{word[cluster_end:]}{word[:cluster_end]}ay"

    if letters.isupper():
        return translated.upper()
    if letters.istitle():
        return translated.capitalize()
    return translated


def parse_text(text: str) -> list[str]:
    """Split text into word and non-word tokens without losing separators."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return re.split(f"({_ASCII_WORD.pattern})", text)


def translate_tokens(tokens: list[str]) -> list[str]:
    """Translate word tokens while leaving separators unchanged."""
    return [
        _translate_letters(token) if _ASCII_WORD.fullmatch(token) else token
        for token in tokens
    ]


def format_translation(tokens: list[str]) -> str:
    """Join translated tokens into the final text."""
    return "".join(tokens)


def translate_word(word: str) -> str:
    """Translate ASCII words in *word*, leaving punctuation unchanged."""
    return format_translation(translate_tokens(parse_text(word)))


def translate_text(text: str) -> str:
    """Translate each ASCII word in *text*, preserving punctuation and spacing."""
    return format_translation(translate_tokens(parse_text(text)))


def main() -> None:
    """Run the interactive command-line translator."""
    print("🐷 Pig Latin Translator 🐷")
    text = input("➡️  Enter text to translate: ")
    tokens = parse_text(text)
    translated_tokens = translate_tokens(tokens)
    print(f"✨ Pig Latin: {format_translation(translated_tokens)}")
    print("👋 Thanks for using the Pig Latin Translator!")


if __name__ == "__main__":
    main()
