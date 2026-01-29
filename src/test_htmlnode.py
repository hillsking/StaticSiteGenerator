import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType


class TestHTMLNode(unittest.TestCase):

    ### Tests for HTMLNode class ###
    
    def test_initialization_defaults(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNone(node.props)

    def test_initialization_with_values(self):
        children = [HTMLNode(tag="p"), HTMLNode(tag="a")]
        props = {"class": "my-class", "id": "my-id"}
        node = HTMLNode(tag="div", value="Hello", children=children, props=props)
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(node.children, children)
        self.assertEqual(node.props, props)

    def test_props_to_html(self):
        props = {"class": "my-class", "id": "my-id"}
        node = HTMLNode(props=props)
        self.assertIn(' class="my-class"', node.props_to_html())
        self.assertIn(' id="my-id"', node.props_to_html())

    def test_props_to_html_empty(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        node = HTMLNode(tag="div", value="Content", 
                        children=[HTMLNode(tag="p"), HTMLNode(tag="a")], 
                        props={"class": "my-class"})
        self.assertIn("tag=div", repr(node))
        self.assertIn("value=Content", repr(node))
        self.assertIn("children=", repr(node))
        self.assertIn("props=", repr(node))

    ### Tests for LeafNode subclass ###

    def test_leaf_to_html_p(self):
        self.assertEqual(LeafNode("p", "Hello, world!").to_html(), "<p>Hello, world!</p>")
        self.assertEqual(LeafNode("p", "Hello, world!", {"class": "intro"}).to_html(), 
                         '<p class="intro">Hello, world!</p>')
        self.assertEqual(LeafNode("p", "").to_html(), "<p></p>")
        
    def test_leaf_to_html_no_tag(self):
        self.assertEqual(LeafNode(None, "Just text").to_html(), "Just text")

    def test_leaf_to_html_link(self):
        self.assertEqual(LeafNode("a", "Click here", {"href": "http://example.com"}).to_html(), 
                         '<a href="http://example.com">Click here</a>')
        
    def test_leaf_to_html_missing_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()  # type: ignore - missing argument intented to raise error
        with self.assertRaises(ValueError):
            LeafNode("a", value=None, props={"href": "http://example.com"}).to_html()  # type: ignore - missing argument intented to raise error

    ## Tests for ParentNode subclass ###

    def test_to_html_with_children(self):
        parent_node = ParentNode("div", [LeafNode("span", "child")])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_many_children(self):
        node = ParentNode("p", [LeafNode("b", "Bold text"),
                                LeafNode(None, "Normal text"),
                                LeafNode("i", "italic text"),
                                LeafNode(None, "Normal text"),
                                LeafNode("a", "Link", {"href": "http://example.com"})])
        self.assertEqual(node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text<a href=\"http://example.com\">Link</a></p>")

    def test_to_html_with_grandchildren(self):
        parent_node = ParentNode("div", [ParentNode("span", [LeafNode("b", "grandchild")])])
        self.assertEqual(parent_node.to_html(), "<div><span><b>grandchild</b></span></div>")


class TestTextNodeToHTMLNode(unittest.TestCase):

    # To LeafNode conversion tests
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        node = TextNode("code snippet", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code snippet")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_link_missing_url(self):
        node = TextNode("Click here", TextType.LINK)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.png", "alt": "Alt text"})

    def test_image_missing_url(self):
        node = TextNode("Alt text", TextType.IMAGE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    # Edge cases
    def test_empty_text(self):
        node = TextNode("", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.value, "")

    def test_empty_bold(self):
        node = TextNode("", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "")

    def test_text_with_special_characters(self):
        node = TextNode("Text with <>&\"'", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.value, "Text with <>&\"'")

    def test_link_with_empty_text(self):
        node = TextNode("", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "")

    def test_image_with_empty_alt(self):
        node = TextNode("", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.png", "alt": ""})

    def test_text_type_as_string(self):
        node = TextNode("Some text", "text")  # type: ignore - unsupported type intented to raise error
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
    
    def test_unsupported_text_type(self):
        node = TextNode("Some text", 'unsupported')  # type: ignore - unsupported type intented to raise error
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
