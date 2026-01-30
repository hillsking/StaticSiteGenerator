import unittest
from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node


class TestMarkdownBlocks(unittest.TestCase):
        
    # Tests for markdown_to_blocks function #
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
            """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_empty_markdown(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_only_newlines(self):
        md = "\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_single_block(self):
        md = "This is a single block of text without any newlines."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [md])
    
    def test_leading_trailing_newlines(self):
        md = "\n\nThis is a block with leading and trailing newlines.\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a block with leading and trailing newlines."])

    def test_multiple_consecutive_newlines(self):
        md = "Block one.\n\n\n\nBlock two after multiple newlines."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block one.", "Block two after multiple newlines."])

    def test_blocks_with_only_whitespace(self):
        md = "Block one.\n\n   \n\nBlock two."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block one.", "Block two."])

    # Tests for block_to_block_type function #
    def test_paragraph_block(self):
        block = "This is a simple paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_heading_block(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_code_block(self):
        block = "```\nprint('Hello, World!')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> This is a blockquote.\n> It has multiple lines."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_block_with_no_spaces(self):
        block = ">This is a blockquote without spaces.\n>Another line."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_block_with_mixed_spaces(self):
        block = "> This is a blockquote.\n>Another line with no space."
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list_block(self):
        block = "- Item one\n- Item two\n- Item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_with_asterisk(self):
        block = "* Item one\n* Item two\n* Item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_with_plus(self):
        block = "+ Item one\n+ Item two"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_mixed_markers_still_valid(self):
        # CommonMark allows mixed markers - all are valid list markers
        block = "- Item one\n* Item two\n+ Item three"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list_block(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_starting_from_5(self):
        block = "5. Fifth item\n6. Sixth item\n7. Seventh item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_non_sequential(self):
        block = "1. First\n3. Third\n5. Fifth"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_mixed_list_block(self):
        block = "1. First item\n- Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_with_incorrect_formatting(self):
        block = "```\nThis is not a code block"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_code_block_with_nested_backticks(self):
        block = "```\nprint('Hello, ```World!')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_code_block_with_nested_list_syntax(self):
        block = "```\n- Not a list item\n1. Not an ordered item\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_heading_with_too_many_hashes(self):
        block = "####### This is not a valid heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_with_no_space(self):
        block = "##This is not a valid heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


    # Tests for markdown_to_html_node function #
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html, "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>")
    
    def test_heading(self):
        md = """
# This is a heading
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>This is a heading</h1></div>")

    def test_heading_with_inline(self):
        md = """
## This is a _heading_ with **inline** `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>This is a <i>heading</i> with <b>inline</b> <code>code</code></h2></div>")

    def test_multiple_headings(self):
        md = """
# Heading 1

```
## Heading 2
```

### Heading 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><h1>Heading 1</h1><pre><code>## Heading 2\n</code></pre><h3>Heading 3</h3></div>",
    )
        
    def test_blockquote(self):
        md = """
> This is a quote
> that spans
> multiple lines
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>This is a quote that spans multiple lines</blockquote></div>")
    
    def test_blockquote_with_inline(self):
        md = """
> This is a _quote_ with **inline** `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>This is a <i>quote</i> with <b>inline</b> <code>code</code></blockquote></div>")

    def test_blockquote_no_space_after_marker(self):
        md = ">Quote without space"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>Quote without space</blockquote></div>")

    def test_blockquote_preserves_content_with_gt(self):
        md = "> Math: 5 > 3 and 10 > 7"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>Math: 5 &gt; 3 and 10 &gt; 7</blockquote></div>")

    def test_unordered_list(self):
        md = """
- Item one
- Item **two**
- Item three with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><ul>"
        "<li>Item one</li>"
        "<li>Item <b>two</b></li>"
        "<li>Item three with <i>italic</i></li>"
        "</ul></div>",
    )
        
    def test_ordered_list(self):
        md = """
1. First
2. Second with **bold**
3. Third with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><ol>"
        "<li>First</li>"
        "<li>Second with <b>bold</b></li>"
        "<li>Third with <i>italic</i></li>"
        "</ol></div>",
    )

    def test_unordered_list_asterisk_to_html(self):
        md = "* Item one\n* Item two"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li>Item one</li><li>Item two</li></ul></div>")

    def test_unordered_list_plus_to_html(self):
        md = "+ First\n+ Second"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ul><li>First</li><li>Second</li></ul></div>")

    def test_ordered_list_from_5_to_html(self):
        md = "5. Fifth\n6. Sixth\n7. Seventh"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><ol><li>Fifth</li><li>Sixth</li><li>Seventh</li></ol></div>")
        
    def test_mixed_content(self):
        md = """
Some introductory text.

```
More text after code.
```

> A quote here.
> And some final text.

# Heading 1

Some paragraph text with `inline code` and **bold** text.\n And some more text.

- List item 1
- List item 2 with _italic_

#### Heading 4

The end.
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,
        "<div>"
        "<p>Some introductory text.</p>"
        "<pre><code>More text after code.\n</code></pre>"
        "<blockquote>A quote here. And some final text.</blockquote>"
        "<h1>Heading 1</h1>"
        "<p>Some paragraph text with <code>inline code</code> and <b>bold</b> text. And some more text.</p>"
        "<ul><li>List item 1</li><li>List item 2 with <i>italic</i></li></ul>"
        "<h4>Heading 4</h4>"
        "<p>The end.</p>"
        "</div>",
    )

    # Tests for hard line breaks (two spaces + \n) #
    def test_hard_line_break_simple(self):
        md = "Line 1  \nLine 2"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Line 1<br />Line 2</p></div>")

    def test_hard_line_break_multiple(self):
        md = "Line 1  \nLine 2  \nLine 3"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Line 1<br />Line 2<br />Line 3</p></div>")

    def test_hard_line_break_with_bold(self):
        md = "**Bold text**  \nNext line"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p><b>Bold text</b><br />Next line</p></div>")

    def test_hard_line_break_with_italic(self):
        md = "_Italic_  \n**Bold**  \n`code`"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p><i>Italic</i><br /><b>Bold</b><br /><code>code</code></p></div>")

    def test_hard_line_break_mixed_with_soft(self):
        md = "Soft\nLine 1  \nHard break  \nLine 2"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Soft Line 1<br />Hard break<br />Line 2</p></div>")

    def test_hard_line_break_in_blockquote(self):
        md = "> Quote line 1  \n> Quote line 2"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><blockquote>Quote line 1<br />Quote line 2</blockquote></div>")

    def test_hard_line_break_with_link(self):
        md = "[Link](https://example.com)  \nNext line"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><p><a href="https://example.com">Link</a><br />Next line</p></div>')

    def test_soft_line_break_still_works(self):
        md = "Line 1\nLine 2\nLine 3"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Line 1 Line 2 Line 3</p></div>")

    def test_hard_line_break_address_example(self):
        md = "John Doe  \n123 Main St  \nNew York, NY 10001"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>John Doe<br />123 Main St<br />New York, NY 10001</p></div>")

    # Tests for code blocks with language specification #
    def test_code_block_with_python_language(self):
        md = "```python\ndef hello():\n    print('world')\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><pre><code>def hello():\n    print(&#x27;world&#x27;)\n</code></pre></div>")

    def test_code_block_with_javascript_language(self):
        md = "```javascript\nconsole.log('hello');\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><pre><code>console.log(&#x27;hello&#x27;);\n</code></pre></div>")

    def test_code_block_with_go_language(self):
        md = "```go\nfunc main() {\n    fmt.Println(\"Hello\")\n}\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, '<div><pre><code>func main() {\n    fmt.Println(&quot;Hello&quot;)\n}\n</code></pre></div>')

    def test_code_block_without_language_still_works(self):
        md = "```\nplain code\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><pre><code>plain code\n</code></pre></div>")

    def test_code_block_with_language_preserves_formatting(self):
        md = "```python\nif True:\n    # comment\n    x = **not bold**\n    y = _not italic_\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><pre><code>if True:\n    # comment\n    x = **not bold**\n    y = _not italic_\n</code></pre></div>")

    def test_code_block_detection_with_language(self):
        block_with_lang = "```python\ncode\n```"
        block_without_lang = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block_with_lang), BlockType.CODE)
        self.assertEqual(block_to_block_type(block_without_lang), BlockType.CODE)

    # Tests for markdown_to_blocks with code blocks containing empty lines #
    def test_code_block_with_empty_lines_stays_single_block(self):
        md = """Text before.

```python
def hello():
    print("line 1")

    print("line 2")
```

Text after."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(len(blocks), 3)
        self.assertTrue(blocks[1].startswith('```python'))
        self.assertTrue(blocks[1].endswith('```'))
        self.assertIn('\n\n', blocks[1])  # Empty line preserved inside code block

    def test_multiple_code_blocks_with_empty_lines(self):
        md = """```python
code1

code2
```

```javascript
code3

code4
```"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(len(blocks), 2)

    def test_regular_paragraphs_still_split_correctly(self):
        md = """Para 1

Para 2

Para 3"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0], 'Para 1')
        self.assertEqual(blocks[1], 'Para 2')
        self.assertEqual(blocks[2], 'Para 3')
