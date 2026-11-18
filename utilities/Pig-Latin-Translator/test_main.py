"""Unittest checks for the Pig Latin translator."""

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("main.py")
SPEC = importlib.util.spec_from_file_location("pig_latin_translator", MODULE_PATH)
translator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = translator
with redirect_stdout(io.StringIO()) as import_output:
    SPEC.loader.exec_module(translator)


class PigLatinTranslatorTests(unittest.TestCase):
    def test_import_does_not_start_cli(self):
        self.assertEqual(import_output.getvalue(), "")

    def test_translation_examples(self):
        cases = [
            ("apple", "appleway"),
            ("hello", "ellohay"),
            ("string", "ingstray"),
            ("quick", "ickquay"),
            ("yellow", "ellowyay"),
            ("rhythm", "ythmrhay"),
            ("Apple", "Appleway"),
            ("QUICK", "ICKQUAY"),
            ("Hello, world!", "Ellohay, orldway!"),
            ("Hello,\tworld!\n", "Ellohay,\torldway!\n"),
            ("café", "afcayé"),
            ("", ""),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(translator.translate_text(text), expected)

    def test_parse_translate_and_format_responsibilities(self):
        tokens = translator.parse_text("Hello,  world!")
        self.assertEqual(tokens, ["", "Hello", ",  ", "world", "!"])
        translated_tokens = translator.translate_tokens(tokens)
        self.assertEqual(
            translated_tokens, ["", "Ellohay", ",  ", "orldway", "!"]
        )
        self.assertEqual(
            translator.format_translation(translated_tokens), "Ellohay,  orldway!"
        )

    def test_translate_word_preserves_punctuation(self):
        self.assertEqual(translator.translate_word("(string!)"), "(ingstray!)")

    def test_text_functions_reject_non_strings(self):
        for function in (
            translator.parse_text,
            translator.translate_word,
            translator.translate_text,
        ):
            with self.subTest(function=function.__name__):
                with self.assertRaises(TypeError):
                    function(None)

    def test_cli_prints_translation_and_goodbye(self):
        output = io.StringIO()
        with patch("builtins.input", return_value="Hello, world!"):
            with redirect_stdout(output):
                translator.main()

        self.assertIn("✨ Pig Latin: Ellohay, orldway!", output.getvalue())
        self.assertIn(
            "👋 Thanks for using the Pig Latin Translator!", output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
