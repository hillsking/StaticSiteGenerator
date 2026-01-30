import unittest
from textnode import TextNode, TextType
from inline_markdown import create_nodes_by_delimiter, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestCreateNodesByDelimiter(unittest.TestCase):

    ### Direct tests for create_nodes_by_delimiter function ###

    def test_empty_string(self):
        result = create_nodes_by_delimiter("")
        self.assertEqual(result, [])

    def test_plain_text_no_delimiters(self):
        result = create_nodes_by_delimiter("plain text")
        self.assertEqual(result, [TextNode("plain text", TextType.TEXT)])

    def test_single_bold(self):
        result = create_nodes_by_delimiter("**bold**")
        self.assertEqual(result, [TextNode("bold", TextType.BOLD)])

    def test_single_italic(self):
        result = create_nodes_by_delimiter("_italic_")
        self.assertEqual(result, [TextNode("italic", TextType.ITALIC)])

    def test_single_code(self):
        result = create_nodes_by_delimiter("`code`")
        self.assertEqual(result, [TextNode("code", TextType.CODE)])

    def test_bold_with_text_before(self):
        result = create_nodes_by_delimiter("text **bold**")
        self.assertEqual(result, [
            TextNode("text ", TextType.TEXT),
            TextNode("bold", TextType.BOLD)
        ])

    def test_bold_with_text_after(self):
        result = create_nodes_by_delimiter("**bold** text")
        self.assertEqual(result, [
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ])

    def test_bold_with_text_both_sides(self):
        result = create_nodes_by_delimiter("before **bold** after")
        self.assertEqual(result, [
            TextNode("before ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" after", TextType.TEXT)
        ])

    def test_multiple_bold(self):
        result = create_nodes_by_delimiter("**first** text **second**")
        self.assertEqual(result, [
            TextNode("first", TextType.BOLD),
            TextNode(" text ", TextType.TEXT),
            TextNode("second", TextType.BOLD)
        ])

    def test_adjacent_bold(self):
        result = create_nodes_by_delimiter("**first****second**")
        self.assertEqual(result, [
            TextNode("first", TextType.BOLD),
            TextNode("second", TextType.BOLD)
        ])

    def test_unmatched_opening_delimiter(self):
        result = create_nodes_by_delimiter("**unmatched")
        self.assertEqual(result, [TextNode("**unmatched", TextType.TEXT)])

    def test_unmatched_closing_delimiter(self):
        result = create_nodes_by_delimiter("unmatched**")
        self.assertEqual(result, [TextNode("unmatched**", TextType.TEXT)])

    def test_empty_between_delimiters(self):
        result = create_nodes_by_delimiter("****")
        self.assertEqual(result, [TextNode("****", TextType.TEXT)])

    def test_nested_italic_in_bold(self):
        result = create_nodes_by_delimiter("**bold _italic_ bold**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" bold", TextType.TEXT)
            ])
        ])

    def test_nested_bold_in_italic(self):
        result = create_nodes_by_delimiter("_italic **bold** italic_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("italic ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" italic", TextType.TEXT)
            ])
        ])

    def test_code_with_underscores_not_parsed(self):
        result = create_nodes_by_delimiter("`code_with_underscores`")
        self.assertEqual(result, [TextNode("code_with_underscores", TextType.CODE)])

    def test_code_with_bold_markers_not_parsed(self):
        result = create_nodes_by_delimiter("`code **bold** here`")
        self.assertEqual(result, [TextNode("code **bold** here", TextType.CODE)])

    def test_mixed_delimiters(self):
        result = create_nodes_by_delimiter("**bold** and _italic_ and `code`")
        self.assertEqual(result, [
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE)
        ])

    def test_only_nested_content(self):
        result = create_nodes_by_delimiter("**_nested_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("nested", TextType.ITALIC)
            ])
        ])

    def test_triple_adjacent(self):
        result = create_nodes_by_delimiter("**a****b****c**")
        self.assertEqual(result, [
            TextNode("a", TextType.BOLD),
            TextNode("b", TextType.BOLD),
            TextNode("c", TextType.BOLD)
        ])

    def test_single_character_content(self):
        result = create_nodes_by_delimiter("**x**")
        self.assertEqual(result, [TextNode("x", TextType.BOLD)])

    def test_whitespace_only_content(self):
        result = create_nodes_by_delimiter("** **")
        self.assertEqual(result, [TextNode(" ", TextType.BOLD)])

    def test_nested_same_type_not_supported(self):
        result = create_nodes_by_delimiter("**outer **inner** outer**")
        self.assertEqual(result, [
            TextNode("outer ", TextType.BOLD),
            TextNode("inner", TextType.TEXT),
            TextNode(" outer", TextType.BOLD)
        ])

    def test_all_three_delimiter_types(self):
        result = create_nodes_by_delimiter("start **bold** mid _italic_ end `code` fin")
        self.assertEqual(result, [
            TextNode("start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" mid ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" fin", TextType.TEXT)
        ])

    def test_delimiter_priority_bold_found_first(self):
        result = create_nodes_by_delimiter("**bold _mix**_")
        self.assertEqual(result, [
            TextNode("bold _mix", TextType.BOLD),
            TextNode("_", TextType.TEXT)
        ])

    def test_complex_nesting(self):
        result = create_nodes_by_delimiter("**I like _Tolkien_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("I like ", TextType.TEXT),
                TextNode("Tolkien", TextType.ITALIC)
            ])
        ])

    def test_multiple_nested_in_one_outer(self):
        result = create_nodes_by_delimiter("**first _a_ second _b_ third**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("first ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" second ", TextType.TEXT),
                TextNode("b", TextType.ITALIC),
                TextNode(" third", TextType.TEXT)
            ])
        ])


class TestInlineMarkdown(unittest.TestCase):
    
    ### Tests for split_nodes_delimiter function ###
    def test_split_nodes_delimiter_basic(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_no_delimiter(self):
        nodes = [TextNode("This is plain text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_multiple(self):
        nodes = [TextNode("**Bold1** and **Bold2**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
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
        result = split_nodes_delimiter(nodes)
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
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("Bold1", TextType.BOLD),
            TextNode("Bold2", TextType.BOLD)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_leading_trailing(self):
        nodes = [TextNode("**Bold at start** and some text **Bold at end**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("Bold at start", TextType.BOLD),
            TextNode(" and some text ", TextType.TEXT),
            TextNode("Bold at end", TextType.BOLD)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_only_delimited(self):
        nodes = [TextNode("**Only bold text**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [TextNode("Only bold text", TextType.BOLD)]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_italic(self):
        nodes = [TextNode("This is _italic_ text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_code(self):
        nodes = [TextNode("Here is `code` snippet", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" snippet", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_mixed_delimiters(self):
        nodes = [TextNode("This is _italic_ and **bold**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold", TextType.BOLD)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_code_and_italic(self):
        nodes = [TextNode("Here is `code` and _italic_", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_multiple_old_nodes_with_unmatched(self):
        nodes = [
            TextNode("This is **bold** text", TextType.TEXT),
            TextNode("This is _italic text", TextType.TEXT)
        ]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
            TextNode("This is _italic text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_empty_old_nodes(self):
        nodes = []
        result = split_nodes_delimiter(nodes)  # type: ignore
        expected = []
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_all_types_mixed(self):
        # Updated: processes all delimiters
        nodes = [TextNode("This is **bold** and _italic_", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC)
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_no_text_nodes(self):
        nodes = [TextNode("This is a link", TextType.LINK, "https://example.com")]
        result = split_nodes_delimiter(nodes)
        expected = [TextNode("This is a link", TextType.LINK, "https://example.com")]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_unmatched(self):
        nodes = [TextNode("This is **bold text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [TextNode("This is **bold text", TextType.TEXT)]
        self.assertEqual(result, expected)

    def test_split_nodes_delimiter_empty_between(self):
        nodes = [TextNode("This is **** text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes)
        expected = [TextNode("This is **** text", TextType.TEXT)]
        self.assertEqual(result, expected)

    
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

    ### Tests for URLs with parentheses ###
    def test_extract_markdown_links_url_with_parens(self):
        self.assertEqual(extract_markdown_links("[Python](https://en.wikipedia.org/wiki/Python_(programming_language))"),
                        [("Python", "https://en.wikipedia.org/wiki/Python_(programming_language)")])

    def test_extract_markdown_links_url_with_multiple_parens(self):
        self.assertEqual(extract_markdown_links("[API](http://example.com/api_(v2)_ref_(latest))"),
                        [("API", "http://example.com/api_(v2)_ref_(latest)")])

    def test_extract_markdown_images_url_with_parens(self):
        self.assertEqual(extract_markdown_images("![diagram](http://example.com/img_(1).png)"),
                        [("diagram", "http://example.com/img_(1).png")])
    

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

    def test_text_to_textnodes_underscores_in_code(self):
        # Regression test: underscores inside code blocks should NOT be treated as italic
        result = text_to_textnodes("text `variable_name` more")
        self.assertEqual(result, [
            TextNode("text ", TextType.TEXT),
            TextNode("variable_name", TextType.CODE),
            TextNode(" more", TextType.TEXT)
        ])

    def test_text_to_textnodes_complex_code_with_underscores(self):
        # Real-world case that was failing before fix
        result = text_to_textnodes("stats: `vocabulary_richness = unique_words / total_words > 0.15`")
        self.assertEqual(result, [
            TextNode("stats: ", TextType.TEXT),
            TextNode("vocabulary_richness = unique_words / total_words > 0.15", TextType.CODE)
        ])

    def test_text_to_textnodes_italic_and_code_separate(self):
        # Ensure italic still works when not inside code
        result = text_to_textnodes("_italic_ text and `code_with_underscore`")
        self.assertEqual(result, [
            TextNode("italic", TextType.ITALIC),
            TextNode(" text and ", TextType.TEXT),
            TextNode("code_with_underscore", TextType.CODE)
        ])

    ### Edge case tests for nested formatting ###
    def test_nested_italic_in_bold(self):
        result = text_to_textnodes("**bold with _italic_ inside**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold with ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" inside", TextType.TEXT)
            ])
        ])

    def test_nested_bold_in_italic(self):
        result = text_to_textnodes("_italic with **bold** inside_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("italic with ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" inside", TextType.TEXT)
            ])
        ])

    def test_nested_multiple_adjacent_in_bold(self):
        result = text_to_textnodes("**text _a_ and _b_ end**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("text ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("b", TextType.ITALIC),
                TextNode(" end", TextType.TEXT)
            ])
        ])

    def test_nested_at_start_and_end_of_bold(self):
        result = text_to_textnodes("**_start_ middle _end_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("start", TextType.ITALIC),
                TextNode(" middle ", TextType.TEXT),
                TextNode("end", TextType.ITALIC)
            ])
        ])

    def test_nested_only_italic_in_bold(self):
        result = text_to_textnodes("**_only italic_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("only italic", TextType.ITALIC)
            ])
        ])

    def test_nested_only_bold_in_italic(self):
        result = text_to_textnodes("_**only bold**_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("only bold", TextType.BOLD)
            ])
        ])

    def test_triple_nesting_bold_italic_bold(self):
        # First ** matches with the ** after "middle ", not the innermost one
        result = text_to_textnodes("**outer _middle **inner** still middle_ outer**")
        self.assertEqual(result, [
            TextNode("outer _middle ", TextType.BOLD),
            TextNode("inner", TextType.TEXT),
            TextNode(" still middle_ outer", TextType.BOLD)
        ])

    def test_triple_nesting_italic_bold_italic(self):
        # First _ matches with the _ after "middle ", not the outermost one
        result = text_to_textnodes("_outer **middle _inner_ still middle** outer_")
        self.assertEqual(result, [
            TextNode("outer **middle ", TextType.ITALIC),
            TextNode("inner", TextType.TEXT),
            TextNode(" still middle** outer", TextType.ITALIC)
        ])

    def test_nested_with_text_before_and_after(self):
        result = text_to_textnodes("before **bold _italic_ bold** after")
        self.assertEqual(result, [
            TextNode("before ", TextType.TEXT),
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" bold", TextType.TEXT)
            ]),
            TextNode(" after", TextType.TEXT)
        ])

    def test_nested_adjacent_outer_elements(self):
        result = text_to_textnodes("**bold _a_****bold _b_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("a", TextType.ITALIC)
            ]),
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("b", TextType.ITALIC)
            ])
        ])

    def test_nested_multiple_same_type_not_nested(self):
        result = text_to_textnodes("**bold _a_ text _b_ end**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold ", TextType.TEXT),
                TextNode("a", TextType.ITALIC),
                TextNode(" text ", TextType.TEXT),
                TextNode("b", TextType.ITALIC),
                TextNode(" end", TextType.TEXT)
            ])
        ])

    def test_code_with_nested_delimiters_not_parsed(self):
        result = text_to_textnodes("`code with ** bold ** and _ italic _`")
        self.assertEqual(result, [
            TextNode("code with ** bold ** and _ italic _", TextType.CODE)
        ])

    def test_code_inside_bold_no_nesting_in_code(self):
        result = text_to_textnodes("**bold with `code_here` bold**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold with ", TextType.TEXT),
                TextNode("code_here", TextType.CODE),
                TextNode(" bold", TextType.TEXT)
            ])
        ])

    def test_nested_with_unmatched_inner_delimiter(self):
        # Unmatched _ remains as text; no nesting so simple form is used
        result = text_to_textnodes("**bold with _italic text**")
        self.assertEqual(result, [
            TextNode("bold with _italic text", TextType.BOLD)
        ])

    def test_nested_real_world_tolkien_example(self):
        result = text_to_textnodes("**I like _Tolkien_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("I like ", TextType.TEXT),
                TextNode("Tolkien", TextType.ITALIC)
            ])
        ])

    def test_nested_real_world_complex_example(self):
        result = text_to_textnodes("_**not** understand_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("not", TextType.BOLD),
                TextNode(" understand", TextType.TEXT)
            ])
        ])

    def test_nested_empty_outer_with_inner_content(self):
        result = text_to_textnodes("**_text_**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("text", TextType.ITALIC)
            ])
        ])

    def test_nested_boundary_case_immediate_nesting(self):
        result = text_to_textnodes("_**x**_")
        self.assertEqual(result, [
            TextNode("", TextType.ITALIC, children=[
                TextNode("x", TextType.BOLD)
            ])
        ])

    def test_complex_multi_nesting_with_plain_text(self):
        # First ** matches with the ** after "_italic ", not the final one
        result = text_to_textnodes("start **bold _italic **bold2** italic_ bold** end")
        self.assertEqual(result, [
            TextNode("start ", TextType.TEXT),
            TextNode("bold _italic ", TextType.BOLD),
            TextNode("bold2", TextType.TEXT),
            TextNode(" italic_ bold", TextType.BOLD),
            TextNode(" end", TextType.TEXT)
        ])

    def test_nested_with_special_characters(self):
        result = text_to_textnodes("**bold <>&\" _italic <>&\"_ bold**")
        self.assertEqual(result, [
            TextNode("", TextType.BOLD, children=[
                TextNode("bold <>&\" ", TextType.TEXT),
                TextNode("italic <>&\"", TextType.ITALIC),
                TextNode(" bold", TextType.TEXT)
            ])
        ])

    def test_deeply_nested_four_levels(self):
        # First ** matches with second **, then continues parsing
        result = text_to_textnodes("**a _b **c _d_ c** b_ a**")
        self.assertEqual(result, [
            TextNode("a _b ", TextType.BOLD),
            TextNode("c ", TextType.TEXT),
            TextNode("d", TextType.ITALIC),
            TextNode(" c", TextType.TEXT),
            TextNode(" b_ a", TextType.BOLD)
        ])





