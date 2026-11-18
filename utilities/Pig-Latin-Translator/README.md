# Pig Latin Translator

A standard-library Python utility that translates ASCII English words into
Pig Latin while preserving punctuation, whitespace, and common capitalization.
Its parsing, translation, and formatting functions can also be imported from
`main.py`.

## Run

From the repository root, run:

```bash
python3 utilities/Pig-Latin-Translator/main.py
```

Enter a line of text when prompted. To run this project's tests:

```bash
python3 -m unittest discover -s utilities/Pig-Latin-Translator -p "test_*.py"
```

## Examples

| Input | Output |
|---|---|
| `Hello, world!` | `Ellohay, orldway!` |
| `quick question` | `ickquay estionquay` |
| `Apple` | `Appleway` |
| `QUICK` | `ICKQUAY` |
| `rhythm` | `ythmrhay` |

Words beginning with `a`, `e`, `i`, `o`, or `u` (case-insensitive) receive
`way`. Otherwise, the initial consonant sequence moves to the end and receives
`ay`. In a consonant sequence, `y` is treated as a vowel after the first
letter, and `u` following `q` stays with that `q`. All-uppercase and
title-case words keep those capitalization styles in the result.

## Supported limits

- Only ASCII letters `A-Z` and `a-z` are recognized as word characters.
- Punctuation, digits, whitespace, and non-ASCII characters are preserved;
  they separate ASCII letter sequences and are not translated.
- This is a simple English Pig Latin rule set, not a linguistic analyzer. It
  does not detect proper names or handle language-specific pronunciation.
- The command-line interface translates one line per run. There are no
  third-party dependencies.

Import `translate_word(text)` or `translate_text(text)` from `main.py` to
translate text in another Python program.
