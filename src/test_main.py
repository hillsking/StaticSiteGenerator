import unittest
from main import extract_title


class TestMainFunctions(unittest.TestCase):
    # extract_title tests
    def test_extract_title_with_title(self):
        md = "# My Title\n\nSome content here."
        self.assertEqual(extract_title(md), "My Title")

    def test_extract_title_no_title(self):
        md = "No title here."
        with self.assertRaises(Exception) as context:
            extract_title(md)
        self.assertEqual(str(context.exception), "No title found in markdown.")

    def test_title_inside_text(self):
        md = "This is a # Not a title\n\n# Actual Title\nMore text."
        self.assertEqual(extract_title(md), "Actual Title")