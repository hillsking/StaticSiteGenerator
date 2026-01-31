import unittest
from textnode import TextNode, TextType
from inline_markdown import (
    extract_markdown_images, 
    extract_markdown_links, 
    text_to_textnodes
)


class TestExtractMarkdown(unittest.TestCase):

    def test_extract_markdown_images_valid_image(self):
        self.assertEqual(
            extract_markdown_images("![Alt text](https://example.com/image.png)"),
            ("Alt text", "https://example.com/image.png"))

    def test_extract_markdown_images_empty_alt(self):
        self.assertEqual(
            extract_markdown_images("![](https://example.com/image.png)"),
            ("", "https://example.com/image.png"))

    def test_extract_markdown_images_not_at_start(self):
        self.assertEqual(
            extract_markdown_images("text ![Alt](url)"),
            (None, None))

    def test_extract_markdown_images_url_with_nested_parens(self):
        self.assertEqual(
            extract_markdown_images("![diagram](http://example.com/img_(1).png)"),
            ("diagram", "http://example.com/img_(1).png"))

    def test_extract_markdown_links_valid_link(self):
        self.assertEqual(
            extract_markdown_links("[link text](https://example.com)"),
            ("link text", "https://example.com"))

    def test_extract_markdown_links_empty_text(self):
        self.assertEqual(
            extract_markdown_links("[](https://example.com)"),
            ("", "https://example.com"))

    def test_extract_markdown_links_not_at_start(self):
        self.assertEqual(
            extract_markdown_links("text [link](url)"),
            (None, None))

    def test_extract_markdown_links_url_with_nested_parens(self):
        self.assertEqual(
            extract_markdown_links("[Python](https://en.wikipedia.org/wiki/Python_(programming_language))"),
            ("Python", "https://en.wikipedia.org/wiki/Python_(programming_language)"))

    def test_extract_markdown_links_url_with_multiple_nested_parens(self):
        self.assertEqual(
            extract_markdown_links("[API](http://example.com/api_(v2)_ref_(latest))"),
            ("API", "http://example.com/api_(v2)_ref_(latest)"))


class TestTextToTextnodes(unittest.TestCase):
    """Tests for text_to_textnodes function."""

    # Basic cases
    def test_text_to_textnodes_empty_string(self):
        self.assertEqual(text_to_textnodes(""), [])

    def test_text_to_textnodes_plain_text(self):
        self.assertEqual(
            text_to_textnodes("plain text"),
            [TextNode("plain text", TextType.TEXT)])

    def test_text_to_textnodes_whitespace_only(self):
        self.assertEqual(
            text_to_textnodes("     "),
            [TextNode("     ", TextType.TEXT)])

    # Single formatting
    def test_text_to_textnodes_single_bold(self):
        self.assertEqual(
            text_to_textnodes("**bold**"),
            [TextNode("bold", TextType.BOLD)])

    def test_text_to_textnodes_single_italic(self):
        self.assertEqual(
            text_to_textnodes("_italic_"),
            [TextNode("italic", TextType.ITALIC)])

    def test_text_to_textnodes_single_code(self):
        self.assertEqual(
            text_to_textnodes("`code`"),
            [TextNode("code", TextType.CODE)])

    def test_text_to_textnodes_single_link(self):
        self.assertEqual(
            text_to_textnodes("[link](url)"),
            [TextNode("link", TextType.LINK, "url")])

    def test_text_to_textnodes_single_image(self):
        self.assertEqual(
            text_to_textnodes("![alt](img.png)"),
            [TextNode("alt", TextType.IMAGE, "img.png")])

    # Formatting with surrounding text
    def test_text_to_textnodes_bold_with_text_before(self):
        self.assertEqual(
            text_to_textnodes("text **bold**"),
            [TextNode("text ", TextType.TEXT), TextNode("bold", TextType.BOLD)])

    def test_text_to_textnodes_bold_with_text_after(self):
        self.assertEqual(
            text_to_textnodes("**bold** text"),
            [TextNode("bold", TextType.BOLD), TextNode(" text", TextType.TEXT)])

    def test_text_to_textnodes_bold_with_text_both_sides(self):
        self.assertEqual(
            text_to_textnodes("before **bold** after"),
            [TextNode("before ", TextType.TEXT), 
             TextNode("bold", TextType.BOLD), 
             TextNode(" after", TextType.TEXT)])

    # Multiple formatting
    def test_text_to_textnodes_multiple_bold(self):
        self.assertEqual(
            text_to_textnodes("**first** text **second**"),
            [TextNode("first", TextType.BOLD),
             TextNode(" text ", TextType.TEXT),
             TextNode("second", TextType.BOLD)])

    def test_text_to_textnodes_adjacent_bold(self):
        self.assertEqual(
            text_to_textnodes("**first****second**"),
            [TextNode("first", TextType.BOLD), TextNode("second", TextType.BOLD)])

    def test_text_to_textnodes_mixed_formatting(self):
        self.assertEqual(
            text_to_textnodes("**bold** and _italic_ and `code`"),
            [TextNode("bold", TextType.BOLD),
             TextNode(" and ", TextType.TEXT),
             TextNode("italic", TextType.ITALIC),
             TextNode(" and ", TextType.TEXT),
             TextNode("code", TextType.CODE)])

    def test_text_to_textnodes_all_formatting_types(self):
        self.assertEqual(
            text_to_textnodes("**Bold**_Italic_`Code`[Link](url)![Image](img.png)"),
            [TextNode("Bold", TextType.BOLD),
             TextNode("Italic", TextType.ITALIC),
             TextNode("Code", TextType.CODE),
             TextNode("Link", TextType.LINK, "url"),
             TextNode("Image", TextType.IMAGE, "img.png")])

    # Unmatched delimiters
    def test_text_to_textnodes_unmatched_opening_delimiter(self):
        self.assertEqual(
            text_to_textnodes("**unmatched"),
            [TextNode("**unmatched", TextType.TEXT)])

    def test_text_to_textnodes_unmatched_closing_delimiter(self):
        self.assertEqual(
            text_to_textnodes("unmatched**"),
            [TextNode("unmatched**", TextType.TEXT)])

    def test_text_to_textnodes_empty_between_delimiters(self):
        self.assertEqual(
            text_to_textnodes("****"),
            [TextNode("****", TextType.TEXT)])

    # Code blocks don't parse inner content
    def test_text_to_textnodes_code_preserves_underscores(self):
        self.assertEqual(
            text_to_textnodes("`code_with_underscores`"),
            [TextNode("code_with_underscores", TextType.CODE)])

    def test_text_to_textnodes_code_preserves_bold_markers(self):
        self.assertEqual(
            text_to_textnodes("`code **bold** here`"),
            [TextNode("code **bold** here", TextType.CODE)])

    def test_text_to_textnodes_code_with_surrounding_text(self):
        self.assertEqual(
            text_to_textnodes("text `variable_name` more"),
            [TextNode("text ", TextType.TEXT),
             TextNode("variable_name", TextType.CODE),
             TextNode(" more", TextType.TEXT)])

    # Nested formatting
    def test_text_to_textnodes_nested_italic_in_bold(self):
        self.assertEqual(
            text_to_textnodes("**bold _italic_ bold**"),
            [TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" bold", TextType.TEXT)])])

    def test_text_to_textnodes_nested_bold_in_italic(self):
        self.assertEqual(
            text_to_textnodes("_italic **bold** italic_"),
            [TextNode("", TextType.ITALIC, children=[
                TextNode("italic ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" italic", TextType.TEXT)])])

    def test_text_to_textnodes_nested_only_italic_in_bold(self):
        self.assertEqual(
            text_to_textnodes("**_only italic_**"),
            [TextNode("", TextType.BOLD, children=[
                TextNode("only italic", TextType.ITALIC)])])

    def test_text_to_textnodes_nested_code_in_bold(self):
        self.assertEqual(
            text_to_textnodes("**bold with `code` bold**"),
            [TextNode("", TextType.BOLD, children=[
                TextNode("bold with ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" bold", TextType.TEXT)])])

    def test_text_to_textnodes_nested_multiple_italic_in_bold(self):
        self.assertEqual(
            text_to_textnodes("**text _a_ and _b_ end**"),
            [TextNode("", TextType.BOLD, children=[
                TextNode("text ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.ITALIC),
                TextNode(" end", TextType.TEXT)])])

    def test_text_to_textnodes_nested_with_surrounding_text(self):
        self.assertEqual(
            text_to_textnodes("before **bold _italic_ bold** after"),
            [TextNode("before ", TextType.TEXT),
             TextNode("", TextType.BOLD, children=[
                 TextNode("bold ", TextType.TEXT),
                 TextNode("italic", TextType.ITALIC),
                 TextNode(" bold", TextType.TEXT)]),
             TextNode(" after", TextType.TEXT)])

    # Links and images with nested formatting
    def test_text_to_textnodes_link_nested_in_bold(self):
        result = text_to_textnodes("**bold [link](url)**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("link", TextType.LINK, "url")])])

    def test_text_to_textnodes_bold_nested_in_link(self):
        result = text_to_textnodes("[Why **Glorfindel**](/blog)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="/blog", children=[
                TextNode("Why ", TextType.TEXT),
                TextNode("Glorfindel", TextType.BOLD)])])

    def test_text_to_textnodes_italic_nested_in_link(self):
        result = text_to_textnodes("[The _Ring_](/ring)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="/ring", children=[
                TextNode("The ", TextType.TEXT),
                TextNode("Ring", TextType.ITALIC)])])

    # Real-world examples
    def test_text_to_textnodes_nested_italic_in_edge_bold(self):
        self.assertEqual(
            text_to_textnodes("**I like _Tolkien_**"),
            [TextNode("", TextType.BOLD, children=[
                TextNode("I like ", TextType.TEXT),
                TextNode("Tolkien", TextType.ITALIC)])])

    def test_text_to_textnodes_nested_bold_in_edge_italic(self):
        self.assertEqual(
            text_to_textnodes("_**not** understand_"),
            [TextNode("", TextType.ITALIC, children=[
                TextNode("not", TextType.BOLD),
                TextNode(" understand", TextType.TEXT)])])

    def test_text_to_textnodes_link_in_bold(self):
        result = text_to_textnodes("**course on [Boot.dev](https://boot.dev)**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("course on ", TextType.TEXT),
                TextNode("Boot.dev", TextType.LINK, "https://boot.dev")])])

    def test_text_to_textnodes_link_url_with_parens(self):
        result = text_to_textnodes("[link](http://site.com/path_(parens)_ok)")
        self.assertEqual(result, [
            TextNode("link", TextType.LINK, "http://site.com/path_(parens)_ok")])

    def test_text_to_textnodes_complex_all_types_mixed(self):
        result = text_to_textnodes("This is **bold** and _italic_ with [link](url) and ![img](pic.png).")
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
            TextNode(" and ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "pic.png"),
            TextNode(".", TextType.TEXT)])

    def test_text_to_textnodes_triple_nesting_bold_in_italic_in_link(self):
        result = text_to_textnodes("[text _with **triple** nesting_](/url)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="/url", children=[
                TextNode("text ", TextType.TEXT),
                TextNode("", TextType.ITALIC, children=[
                    TextNode("with ", TextType.TEXT),
                    TextNode("triple", TextType.BOLD),
                    TextNode(" nesting", TextType.TEXT)])])])

    def test_text_to_textnodes_multiple_nested_in_link(self):
        result = text_to_textnodes("[**bold** and _italic_ and `code`](/url)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="/url", children=[
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE)])])

    def test_text_to_textnodes_adjacent_nested_structures(self):
        result = text_to_textnodes("**_bold-italic_****[link](url)**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold-italic", TextType.ITALIC)]),
            TextNode("", TextType.BOLD, children=[
                TextNode("link", TextType.LINK, "url")])])

    def test_text_to_textnodes_deep_nesting_multiple_text_nodes(self):
        result = text_to_textnodes("**outer _inner `code` more_ outer**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("outer ", TextType.TEXT),
                TextNode("", TextType.ITALIC, children=[
                    TextNode("inner ", TextType.TEXT),
                    TextNode("code", TextType.CODE),
                    TextNode(" more", TextType.TEXT)]),
                TextNode(" outer", TextType.TEXT)])])

    def test_text_to_textnodes_link_with_nested_complex_formatting(self):
        result = text_to_textnodes("[Click **here** for _more_ info](https://example.com/page_(info))")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="https://example.com/page_(info)", children=[
                TextNode("Click ", TextType.TEXT),
                TextNode("here", TextType.BOLD),
                TextNode(" for ", TextType.TEXT),
                TextNode("more", TextType.ITALIC),
                TextNode(" info", TextType.TEXT)])])

    def test_text_to_textnodes_consecutive_nested_with_text(self):
        result = text_to_textnodes("Start **_nest1_** middle **_nest2_** end")
        self.assertEqual(result, [
            TextNode("Start ", TextType.TEXT),
            TextNode("", TextType.BOLD, children=[
                TextNode("nest1", TextType.ITALIC)]),
            TextNode(" middle ", TextType.TEXT),
            TextNode("", TextType.BOLD, children=[
                TextNode("nest2", TextType.ITALIC)]),
            TextNode(" end", TextType.TEXT)])

    def test_text_to_textnodes_image_inside_link(self):
        """[![alt](img)](url) -> clickable image"""
        result = text_to_textnodes("[![alt](image.png)](https://example.com)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="https://example.com", children=[
                TextNode("alt", TextType.IMAGE, link="image.png")])])

    def test_text_to_textnodes_image_inside_link_with_surrounding_text(self):
        result = text_to_textnodes("Click [![logo](logo.png)](https://home.com) here")
        self.assertEqual(result, [
            TextNode("Click ", TextType.TEXT),
            TextNode("", TextType.LINK, link="https://home.com", children=[
                TextNode("logo", TextType.IMAGE, link="logo.png")]),
            TextNode(" here", TextType.TEXT)])

    def test_text_to_textnodes_image_inside_link_empty_alt(self):
        result = text_to_textnodes("[![](icon.svg)](https://site.com)")
        self.assertEqual(result, [
            TextNode("", TextType.LINK, link="https://site.com", children=[
                TextNode("", TextType.IMAGE, link="icon.svg")])])

    def test_text_to_textnodes_single_strikethrough(self):
        result = text_to_textnodes("~~deleted~~")
        self.assertEqual(result, [TextNode("deleted", TextType.STRIKETHROUGH)])

    def test_text_to_textnodes_strikethrough_with_text(self):
        result = text_to_textnodes("This is ~~deleted~~ text")
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("deleted", TextType.STRIKETHROUGH),
            TextNode(" text", TextType.TEXT)])

    def test_text_to_textnodes_multiple_strikethrough(self):
        result = text_to_textnodes("~~first~~ normal ~~second~~")
        self.assertEqual(result, [
            TextNode("first", TextType.STRIKETHROUGH),
            TextNode(" normal ", TextType.TEXT),
            TextNode("second", TextType.STRIKETHROUGH)])

    def test_text_to_textnodes_strikethrough_nested_in_bold(self):
        result = text_to_textnodes("**bold ~~and strikethrough~~**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("and strikethrough", TextType.STRIKETHROUGH)])])
        
    def test_text_to_textnodes_bold_nested_in_strikethrough(self):
        result = text_to_textnodes("~~deleted **bold** text~~")
        self.assertEqual(result, [
            TextNode("", TextType.STRIKETHROUGH, children=[
                TextNode("deleted ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT)])])

    def test_text_to_textnodes_asterisk_for_italic(self):
        result = text_to_textnodes("*italic*")
        self.assertEqual(result, [TextNode("italic", TextType.ITALIC)])

    def test_text_to_textnodes_asterisk_italic_with_text(self):
        result = text_to_textnodes("some *italic* text")
        self.assertEqual(result, [
            TextNode("some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT)])

    def test_text_to_textnodes_double_underscore_for_bold(self):
        result = text_to_textnodes("__bold__")
        self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

    def test_text_to_textnodes_double_underscore_bold_with_text(self):
        result = text_to_textnodes("some __bold__ text")
        self.assertEqual(result, [
            TextNode("some ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)])

    def test_text_to_textnodes_mixed_bold_delimiters(self):
        result = text_to_textnodes("**bold1** and __bold2__")
        self.assertEqual(result, [
            TextNode("bold1", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold2", TextType.BOLD)])

    def test_text_to_textnodes_mixed_italic_delimiters(self):
        """Both _ and * should work for italic"""
        result = text_to_textnodes("_italic1_ and *italic2*")
        self.assertEqual(result, [
            TextNode("italic1", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic2", TextType.ITALIC)])

    def test_text_to_textnodes_asterisk_italic_in_double_asterisk_bold(self):
        result = text_to_textnodes("**bold *italic text***")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("italic text", TextType.ITALIC)])])

    def test_text_to_textnodes_underscore_italic_in_double_underscore_bold(self):
        result = text_to_textnodes("__bold _italic_ text__")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT)])])

    def test_text_to_textnodes_double_asterisk_bold_in_underscore_italic(self):
        """**bold** inside _italic_ using different delimiters"""
        result = text_to_textnodes("_italic **bold** text_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("italic ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT)])])

    def test_text_to_textnodes_double_underscore_bold_in_asterisk_italic(self):
        """__bold__ inside *italic* using different delimiters"""
        result = text_to_textnodes("*italic __bold__ text*")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("italic ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT)])])


if __name__ == "__main__":
    unittest.main()





