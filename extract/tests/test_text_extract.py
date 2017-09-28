"""Tests for text_extract module."""
import unittest

from extract.text_extract import split_paragraphs, pos_tag, extract_from_sentences


class TextExtractTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = "The dog lives in a house. He saw a plane from the big window. The dog was born in France."
        cls.token2sentence = {
            "dog": {0, 2},
            "house": {0},
            "saw": {1},
            "plane": {1},
            "big_window": {1},
            "bear": {2},
            "live": {0},
            "france": {2}
        }
        cls.tokens = [
            "dog",
            "house",
            "saw",
            "plane",
            "big_window",
            "born",
        ]

    def test_split_paragraphs_big_paragraph(self):
        text = "Hello world.\n\nSecond paragraph.\n\n\n\nThird paragraph."
        self.assertEqual(len(split_paragraphs(text)), 3)

    def test_split_paragraphs_multiline_paragraph(self):
        text = "Hello world.\nSecond line.\n\nSecond paragraph.\n\nThird paragraph."
        self.assertEqual(len(split_paragraphs(text)), 3)

    def test_pos_tag_sentence_number(self):
        sentences = pos_tag(TextExtractTests.text)
        self.assertEqual(len(sentences), 3)

    def test_pos_tag_correct(self):
        sentences = pos_tag(TextExtractTests.text)
        correct = [
            ("The", "DT"),
            ("dog", "NN"),
            ("lives", "VBZ"),
            ("in", "IN"),
            ("a", "DT"),
            ("house", "NN"),
            (".", ".")
        ]
        for (token, tag), (correct_token, correct_tag) in zip(sentences[0].tokens.items(), correct):
            self.assertEqual(token, correct_token)
            self.assertEqual(tag, correct_tag)

    def test_extract_from_sentences(self):
        sentences = pos_tag(TextExtractTests.text)
        token2sentences = extract_from_sentences(sentences)
        self.assertEqual(set(token2sentences), set(TextExtractTests.token2sentence))


if __name__ == "__main__":
    unittest.main()
