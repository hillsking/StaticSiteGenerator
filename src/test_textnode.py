import unittest
from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(TextNode("This is a text node", TextType.BOLD), TextNode("This is a text node", TextType.BOLD))

    def test_not_equal_text(self):
        self.assertNotEqual(TextNode("This is a text node", TextType.BOLD), TextNode("This is a different text node", TextType.BOLD))

    def test_not_equal_type(self):
        self.assertNotEqual(TextNode("This is a text node", TextType.BOLD), TextNode("This is a text node", TextType.ITALIC))

    def test_url_none_vs_value(self):
        self.assertNotEqual(TextNode("This is a link", TextType.LINK, "https://example.com"), TextNode("This is a link", TextType.LINK))
    
    def test_eq_other_object(self):
        self.assertNotEqual(TextNode("This is a text node", TextType.BOLD), "Not a TextNode")

if __name__ == "__main__":
    unittest.main()