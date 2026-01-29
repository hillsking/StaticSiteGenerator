import unittest
from textnode import TextNode, TextType
from inline_markdown import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestInlineMarkdown(unittest.TestCase):
    
    ### Tests for split_nodes_delimiter function ###
    def test_split_nodes_delimiter_basic(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_no_delimiter(self):
        nodes = [TextNode("This is plain text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_multiple(self):
        nodes = [TextNode("**Bold1** and **Bold2**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Bold1", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("Bold2", TextType.BOLD)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_big_old_list(self):
        nodes = [
            TextNode("Start **bold1** middle **bold2** end", TextType.TEXT),
            TextNode("No formatting here", TextType.TEXT),
            TextNode("**Bold3** at the end", TextType.TEXT)
        ]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold1", TextType.BOLD),
            TextNode(" middle ", TextType.TEXT),
            TextNode("bold2", TextType.BOLD),
            TextNode(" end", TextType.TEXT),
            TextNode("No formatting here", TextType.TEXT),
            TextNode("Bold3", TextType.BOLD),
            TextNode(" at the end", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_adjacent(self):
        nodes = [TextNode("**Bold1****Bold2**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Bold1", TextType.BOLD),
            TextNode("Bold2", TextType.BOLD)
        ]
        self.assertEqual(result, expected)
    
    def test_split_nodes_delimiter_leading_trailing(self):
        nodes = [TextNode("**Bold at start** and some text **Bold at end**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Bold at start", TextType.BOLD),
            TextNode(" and some text ", TextType.TEXT),
            TextNode("Bold at end", TextType.BOLD)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_only_delimited(self):
        nodes = [TextNode("**Only bold text**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [TextNode("Only bold text", TextType.BOLD)]
        self.assertEqual(result, expected)
    
    def test_split_nodes_delimiter_italic(self):
        nodes = [TextNode("This is _italic_ text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_code(self):
        nodes = [TextNode("Here is `code` snippet", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" snippet", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_italic_check_with_bold(self):
        nodes = [TextNode("This is _italic_ and **bold**", TextType.TEXT)]
        result_italic = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        expected_italic = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and **bold**", TextType.TEXT)
        ]
        self.assertEqual(result_italic, expected_italic)

    def test_split_nodes_delimiter_code_check_with_italic(self):
        nodes = [TextNode("Here is `code` and _italic_", TextType.TEXT)]
        result_code = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected_code = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and _italic_", TextType.TEXT)
        ]
        self.assertEqual(result_code, expected_code)

    def test_split_nodes_delimiter_multiple_old_nodes_one_incorrect(self):
        nodes = [
            TextNode("This is **bold** text", TextType.TEXT),
            TextNode("This is _italic text", TextType.TEXT)  # Unmatched delimiter
        ]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    def test_split_nodes_delimiter_empty_old_nodes(self):
        nodes = []
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)  # type: ignore
        expected = []
        self.assertEqual(result, expected)
    
    def test_split_nodes_delimiter_mixed_types(self):
        nodes = [TextNode("This is **bold** and _italic_", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and _italic_", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_no_text_nodes(self):
        nodes = [TextNode("This is a link", TextType.LINK, "https://example.com")]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [TextNode("This is a link", TextType.LINK, "https://example.com")]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_unmatched(self):
        nodes = [TextNode("This is **bold text", TextType.TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)

    def test_split_nodes_delimiter_empty_between(self):
        nodes = [TextNode("This is **** text", TextType.TEXT)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(nodes, "**", TextType.BOLD)

    
    ### Tests for extract_markdown_images function ###
    def test_extract_markdown_images_basic(self):
        self.assertEqual(extract_markdown_images("Here is an image ![Alt text](https://example.com/image.png) in markdown."),
                        [("Alt text", "https://example.com/image.png")])
        
    def test_extract_markdown_images_multiple(self):
        self.assertEqual(extract_markdown_images("![Image1](url1) and ![Image2](url2)"),
                        [("Image1", "url1"), ("Image2", "url2")])
    
    def test_extract_markdown_images_no_images(self):
        self.assertEqual(extract_markdown_images("No images here."), [])
    
    def test_extract_markdown_images_empty_alt_text(self):
        self.assertEqual(extract_markdown_images("![ ](https://example.com/image.png)"),
                        [(" ", "https://example.com/image.png")])
        
    def test_extract_markdown_images_no_alt_text(self):
        self.assertEqual(extract_markdown_images("![](https://example.com/image.png)"),
                        [("", "https://example.com/image.png")])
    
    def test_extract_markdown_images_with_link_before(self):
        self.assertEqual(extract_markdown_images("[Link](https://example.com) and ![Alt text](https://example.com/image.png)"),
                        [("Alt text", "https://example.com/image.png")])
    
    ### Tests for extract_markdown_links function ###
    def test_extract_markdown_links_basic(self):
        self.assertEqual(extract_markdown_links("Here is a [link](https://example.com) in markdown."),
                        [("link", "https://example.com")])
        
    def test_extract_markdown_links_multiple(self):
        self.assertEqual(extract_markdown_links("Visit [Google](https://google.com) or [Bing](https://bing.com)"),
                        [("Google", "https://google.com"), ("Bing", "https://bing.com")])
    
    def test_extract_markdown_links_no_links(self):
        self.assertEqual(extract_markdown_links("No links here."), [])
    
    def test_extract_markdown_links_empty_link_text(self):
        self.assertEqual(extract_markdown_links("[](https://example.com)"),
                        [("", "https://example.com")])
        
    def test_extract_markdown_links_with_image_before(self):
        self.assertEqual(extract_markdown_links("![Alt text](https://example.com/image.png) and [link](https://example.com)"),
                        [("link", "https://example.com")])
    

    ### Test for split_nodes_image function ###
    def test_split_nodes_image_basic(self):
        self.assertEqual(split_nodes_image([TextNode("Here is an image ![Alt text](https://example.com/image.png) in markdown.", TextType.TEXT)]), 
                         [TextNode("Here is an image ", TextType.TEXT),
                          TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png"),
                          TextNode(" in markdown.", TextType.TEXT)])
        
    def test_split_nodes_image_multiple(self):
        self.assertEqual(split_nodes_image([TextNode("![Image1](url1) and ![Image2](url2)", TextType.TEXT)]),
                         [TextNode("Image1", TextType.IMAGE, "url1"),
                          TextNode(" and ", TextType.TEXT),
                          TextNode("Image2", TextType.IMAGE, "url2")])
    
    def test_split_nodes_image_no_images(self):
        self.assertEqual(split_nodes_image([TextNode("No images here.", TextType.TEXT)]),
                         [TextNode("No images here.", TextType.TEXT)])
        
    def test_split_nodes_image_mixed_types(self):
        self.assertEqual(split_nodes_image([TextNode("![Image](url) and some **bold** text", TextType.TEXT)]),
                         [TextNode("Image", TextType.IMAGE, "url"),
                          TextNode(" and some **bold** text", TextType.TEXT)])
        
    def test_split_nodes_image_only_image(self):
        self.assertEqual(split_nodes_image([TextNode("![Only image](https://onlyimage.com/image.png)", TextType.TEXT)]),
                         [TextNode("Only image", TextType.IMAGE, "https://onlyimage.com/image.png")])
        
    def test_split_nodes_image_on_edges(self):
        self.assertEqual(split_nodes_image([TextNode("![Start image](https://start.com/image.png) and some text ![End image](https://end.com/image.png)", TextType.TEXT)]),
                         [TextNode("Start image", TextType.IMAGE, "https://start.com/image.png"),
                          TextNode(" and some text ", TextType.TEXT),
                          TextNode("End image", TextType.IMAGE, "https://end.com/image.png")])
        
    def test_split_nodes_image_adjacent(self):
        self.assertEqual(split_nodes_image([TextNode("![Image1](url1)![Image2](url2)", TextType.TEXT)]),
                         [TextNode("Image1", TextType.IMAGE, "url1"),
                          TextNode("Image2", TextType.IMAGE, "url2")])
        
    def test_split_nodes_image_multiple_old_nodes(self):
        self.assertEqual(split_nodes_image([
            TextNode("Here is ![Image1](url1)", TextType.TEXT),
            TextNode("Some text", TextType.TEXT),
            TextNode("![Image2](url2) at the end", TextType.TEXT)
        ]),
        [
            TextNode("Here is ", TextType.TEXT),
            TextNode("Image1", TextType.IMAGE, "url1"),
            TextNode("Some text", TextType.TEXT),
            TextNode("Image2", TextType.IMAGE, "url2"),
            TextNode(" at the end", TextType.TEXT)
        ])

    def test_split_nodes_image_multiple_old_nodes_with_not_text_type(self):
        self.assertEqual(split_nodes_image([
            TextNode("Here is ![Image1](url1)", TextType.TEXT),
            TextNode("A link [here](https://example.com)", TextType.LINK, "https://example.com"),
            TextNode("![Image2](url2) at the end", TextType.TEXT)
        ]),
        [
            TextNode("Here is ", TextType.TEXT),
            TextNode("Image1", TextType.IMAGE, "url1"),
            TextNode("A link [here](https://example.com)", TextType.LINK, "https://example.com"),
            TextNode("Image2", TextType.IMAGE, "url2"),
            TextNode(" at the end", TextType.TEXT)
        ])
    
    def test_split_nodes_image_empty_old_nodes(self):
        self.assertEqual(split_nodes_image([]), [])
    
    def test_split_nodes_image_no_text_nodes(self):
        self.assertEqual(split_nodes_image([TextNode("This is a link", TextType.LINK, "https://example.com")]),
                         [TextNode("This is a link", TextType.LINK, "https://example.com")])
        
    ### Test for split_nodes_link function ###
    def test_split_nodes_link_basic(self):
        self.assertEqual(split_nodes_link([TextNode("Here is a [link](https://example.com) in markdown.", TextType.TEXT)]), 
                         [TextNode("Here is a ", TextType.TEXT),
                          TextNode("link", TextType.LINK, "https://example.com"),
                          TextNode(" in markdown.", TextType.TEXT)])
    
    def test_split_nodes_link_multiple(self):
        self.assertEqual(split_nodes_link([TextNode("Visit [Google](https://google.com) or [Bing](https://bing.com)", TextType.TEXT)]),
                         [TextNode("Visit ", TextType.TEXT),
                          TextNode("Google", TextType.LINK, "https://google.com"),
                          TextNode(" or ", TextType.TEXT),
                          TextNode("Bing", TextType.LINK, "https://bing.com")])
        
    def test_split_nodes_link_no_links(self):
        self.assertEqual(split_nodes_link([TextNode("No links here.", TextType.TEXT)]),
                         [TextNode("No links here.", TextType.TEXT)])
        
    def test_split_nodes_link_mixed_types(self):
        self.assertEqual(split_nodes_link([TextNode("[Link](url) and some _italic_ text", TextType.TEXT)]),
                         [TextNode("Link", TextType.LINK, "url"),
                          TextNode(" and some _italic_ text", TextType.TEXT)])
        
    def test_split_nodes_link_only_link(self):
        self.assertEqual(split_nodes_link([TextNode("[Only link](https://onlylink.com)", TextType.TEXT)]),
                         [TextNode("Only link", TextType.LINK, "https://onlylink.com")])
        
    def test_split_nodes_link_on_edges(self):
        self.assertEqual(split_nodes_link([TextNode("[Start link](https://start.com) and some text [End link](https://end.com)", TextType.TEXT)]),
                         [TextNode("Start link", TextType.LINK, "https://start.com"),
                          TextNode(" and some text ", TextType.TEXT),
                          TextNode("End link", TextType.LINK, "https://end.com")])
        
    def test_split_nodes_link_adjacent(self):
        self.assertEqual(split_nodes_link([TextNode("[Link1](url1)[Link2](url2)", TextType.TEXT)]),
                         [TextNode("Link1", TextType.LINK, "url1"),
                          TextNode("Link2", TextType.LINK, "url2")])
        
    def test_split_nodes_link_multiple_old_nodes(self):
        self.assertEqual(split_nodes_link([
            TextNode("Here is [Link1](url1)", TextType.TEXT),
            TextNode("Some text", TextType.TEXT),
            TextNode("[Link2](url2) at the end", TextType.TEXT)
        ]),
        [
            TextNode("Here is ", TextType.TEXT),
            TextNode("Link1", TextType.LINK, "url1"),
            TextNode("Some text", TextType.TEXT),
            TextNode("Link2", TextType.LINK, "url2"),
            TextNode(" at the end", TextType.TEXT)
        ])
    
    def test_split_nodes_link_multiple_old_nodes_with_not_text_type(self):
        self.assertEqual(split_nodes_link([
            TextNode("Here is [Link1](url1)", TextType.TEXT),
            TextNode("An image ![Alt](image.png)", TextType.IMAGE, "image.png"),
            TextNode("[Link2](url2) at the end", TextType.TEXT)
        ]),
        [
            TextNode("Here is ", TextType.TEXT),
            TextNode("Link1", TextType.LINK, "url1"),
            TextNode("An image ![Alt](image.png)", TextType.IMAGE, "image.png"),
            TextNode("Link2", TextType.LINK, "url2"),
            TextNode(" at the end", TextType.TEXT)
        ])

    def test_split_nodes_link_empty_old_nodes(self):
        self.assertEqual(split_nodes_link([]), [])

    def test_split_nodes_link_no_text_nodes(self):
        self.assertEqual(split_nodes_link([TextNode("This is an image", TextType.IMAGE, "https://example.com/image.png")]),
                         [TextNode("This is an image", TextType.IMAGE, "https://example.com/image.png")])
        

    ### Test for text_to_textnodes function ###
    def test_text_to_textnodes_plain_text(self):
        self.assertEqual(text_to_textnodes("This is plain text."),
                         [TextNode("This is plain text.", TextType.TEXT)])
        
    def test_text_to_textnodes_empty_string(self):
        self.assertEqual(text_to_textnodes(""), [])
        
    def test_text_to_textnodes_basic(self):
        self.assertEqual(text_to_textnodes("This is **bold** and _italic_ text with a [link](https://example.com) and an image ![Alt](https://example.com/image.png)."),
                         [
                             TextNode("This is ", TextType.TEXT),
                             TextNode("bold", TextType.BOLD),
                             TextNode(" and ", TextType.TEXT),
                             TextNode("italic", TextType.ITALIC),
                             TextNode(" text with a ", TextType.TEXT),
                             TextNode("link", TextType.LINK, "https://example.com"),
                             TextNode(" and an image ", TextType.TEXT),
                             TextNode("Alt", TextType.IMAGE, "https://example.com/image.png"),
                             TextNode(".", TextType.TEXT)
                         ])
        
    def test_text_to_textnodes_only_formatting(self):
        self.assertEqual(text_to_textnodes("**Bold** _Italic_ `Code` [Link](url) ![Image](img.png)"),
                         [
                             TextNode("Bold", TextType.BOLD),
                             TextNode(" ", TextType.TEXT),
                             TextNode("Italic", TextType.ITALIC),
                             TextNode(" ", TextType.TEXT),
                             TextNode("Code", TextType.CODE),
                             TextNode(" ", TextType.TEXT),
                             TextNode("Link", TextType.LINK, "url"),
                             TextNode(" ", TextType.TEXT),
                             TextNode("Image", TextType.IMAGE, "img.png")
                         ])
        
    def test_text_to_textnodes_only_whitespace(self):
        self.assertEqual(text_to_textnodes("     "),
                         [TextNode("     ", TextType.TEXT)])
        
    def test_text_to_textnodes_no_text_nodes(self):
        self.assertEqual(text_to_textnodes("**Bold**"),
                         [TextNode("Bold", TextType.BOLD)])
    
    def test_text_to_textnodes_only_formatting_no_plain_text(self):
        self.assertEqual(text_to_textnodes("**Bold**_Italic_`Code`[Link](url)![Image](img.png)"),
                         [
                             TextNode("Bold", TextType.BOLD),
                             TextNode("Italic", TextType.ITALIC),
                             TextNode("Code", TextType.CODE),
                             TextNode("Link", TextType.LINK, "url"),
                             TextNode("Image", TextType.IMAGE, "img.png")
                         ])
        
    
        

    
