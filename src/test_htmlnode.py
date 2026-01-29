import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node, html_escape
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

    ### Tests for void elements (self-closing tags) ###

    def test_leaf_void_element_img(self):
        node = LeafNode("img", "", {"src": "image.png", "alt": "Test image"})
        self.assertEqual(node.to_html(), '<img src="image.png" alt="Test image" />')

    def test_leaf_void_element_img_single_prop(self):
        node = LeafNode("img", "", {"src": "photo.jpg"})
        self.assertEqual(node.to_html(), '<img src="photo.jpg" />')

    def test_leaf_void_element_br(self):
        node = LeafNode("br", "")
        self.assertEqual(node.to_html(), '<br />')

    def test_leaf_void_element_hr(self):
        node = LeafNode("hr", "")
        self.assertEqual(node.to_html(), '<hr />')

    def test_leaf_void_element_input(self):
        node = LeafNode("input", "", {"type": "text", "name": "username"})
        self.assertEqual(node.to_html(), '<input type="text" name="username" />')

    def test_leaf_void_element_meta(self):
        node = LeafNode("meta", "", {"charset": "utf-8"})
        self.assertEqual(node.to_html(), '<meta charset="utf-8" />')

    def test_leaf_void_element_link(self):
        node = LeafNode("link", "", {"rel": "stylesheet", "href": "style.css"})
        self.assertEqual(node.to_html(), '<link rel="stylesheet" href="style.css" />')

    def test_leaf_non_void_elements_still_work(self):
        # Ensure normal elements still use closing tags
        self.assertEqual(LeafNode("p", "text").to_html(), "<p>text</p>")
        self.assertEqual(LeafNode("div", "content").to_html(), "<div>content</div>")
        self.assertEqual(LeafNode("span", "word").to_html(), "<span>word</span>")

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


class TestHTMLEscaping(unittest.TestCase):
    """Tests for HTML escaping to prevent XSS attacks."""

    def test_html_escape_ampersand(self):
        self.assertEqual(html_escape("Tom & Jerry"), "Tom &amp; Jerry")

    def test_html_escape_less_than(self):
        self.assertEqual(html_escape("5 < 10"), "5 &lt; 10")

    def test_html_escape_greater_than(self):
        self.assertEqual(html_escape("10 > 5"), "10 &gt; 5")

    def test_html_escape_double_quote(self):
        self.assertEqual(html_escape('Say "Hello"'), "Say &quot;Hello&quot;")

    def test_html_escape_single_quote(self):
        self.assertEqual(html_escape("It's mine"), "It&#x27;s mine")

    def test_html_escape_all_special_chars(self):
        text = """<script>alert("XSS & 'attack'")</script>"""
        expected = """&lt;script&gt;alert(&quot;XSS &amp; &#x27;attack&#x27;&quot;)&lt;/script&gt;"""
        self.assertEqual(html_escape(text), expected)

    def test_html_escape_order_matters(self):
        text = "A&B<C"
        result = html_escape(text)
        self.assertEqual(result, "A&amp;B&lt;C")

    def test_leaf_node_escapes_content(self):
        node = LeafNode("p", "<script>alert('XSS')</script>")
        self.assertEqual(node.to_html(), "<p>&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;</p>")

    def test_leaf_node_escapes_content_without_tag(self):
        node = LeafNode(None, "<b>Not bold</b>")
        self.assertEqual(node.to_html(), "&lt;b&gt;Not bold&lt;/b&gt;")

    def test_leaf_node_escapes_attributes(self):
        node = LeafNode("a", "Click", {"href": "javascript:alert(\"XSS\")"})
        self.assertEqual(node.to_html(), '<a href="javascript:alert(&quot;XSS&quot;)">Click</a>')

    def test_leaf_node_escapes_special_chars_in_attributes(self):
        node = LeafNode("div", "text", {"data-value": "Tom & Jerry < 100"})
        self.assertEqual(node.to_html(), '<div data-value="Tom &amp; Jerry &lt; 100">text</div>')

    def test_xss_attack_via_content(self):
        malicious_input = '<img src=x onerror="alert(\'XSS\')">'
        node = LeafNode("div", malicious_input)
        html = node.to_html()
        # Verify tags are escaped - should not contain actual HTML tags
        self.assertNotIn("<img", html)
        self.assertIn("&lt;img", html)
        # Check the full escaped output is correct
        self.assertEqual(html, '<div>&lt;img src=x onerror=&quot;alert(&#x27;XSS&#x27;)&quot;&gt;</div>')

    def test_xss_attack_via_attributes(self):
        malicious_url = '" onclick="alert(\'XSS\')" data-x="'
        node = LeafNode("a", "Click", {"href": malicious_url})
        html = node.to_html()
        self.assertIn("&quot;", html)
        self.assertNotIn('" onclick="', html)
