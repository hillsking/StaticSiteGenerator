import re
from enum import Enum
from typing import List
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType
from inline_markdown import text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'
    HORIZONTAL_RULE = 'horizontal_rule'


def markdown_to_blocks(markdown: str) -> List[str]:
    """Parse markdown into blocks, handling fenced code blocks correctly.
        Args: markdown - The markdown text to convert to blocks.
        Returns: A list of markdown blocks.
    """
    blocks: List[str] = []
    lines: List[str] = markdown.split('\n')
    current_block: List[str] = []
    in_code_block: bool = False

    for line in lines:
        # Check if we're entering/exiting a code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_block.append(line)
        elif not in_code_block and line.strip() == '':
            # Empty line outside code block = end of block
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
        else:
            # Regular line or line inside code block
            current_block.append(line)

    # Don't forget the last block
    if current_block:
        blocks.append('\n'.join(current_block))

    return [block.strip() for block in blocks if block.strip()]
    


def block_to_block_type(block: str) -> BlockType:
    """Args: block - The markdown block to determine the type of.
       Returns: The BlockType of the given markdown block."""
    if block.startswith(('# ', '## ', '### ', '#### ', '##### ', '###### ')):
        return BlockType.HEADING
    elif block.startswith('```') and block.endswith('```') and '\n' in block:
        return BlockType.CODE
    elif all(line.startswith('>') for line in block.splitlines()):
        return BlockType.QUOTE
    elif all(line.startswith(("- ", "* ", "+ ")) for line in block.splitlines()):
        return BlockType.UNORDERED_LIST
    elif all(re.match(r'^\d+\. ', line) for line in block.splitlines()):
        return BlockType.ORDERED_LIST
    elif re.match(r'^(-{3,}|\*{3,}|_{3,})$', block.strip()):
        return BlockType.HORIZONTAL_RULE
    else:
        return BlockType.PARAGRAPH
    

def parse_children(text: str) -> List[HTMLNode | LeafNode | ParentNode]:
    """Parse markdown text into HTML nodes.
        Args: text - The markdown text to parse into HTMLNodes.
        Returns: A list of HTMLNodes representing the parsed text.
    """
    if not text:
        return []

    # Split by hard line breaks (two spaces + newline)
    parts = text.split('  \n')
    result: List[HTMLNode | LeafNode | ParentNode] = []

    for i, part in enumerate(parts):
        if part:
            # Normalize whitespace (soft line breaks become spaces)
            result.extend([text_node_to_html_node(tn) for tn in text_to_textnodes(' '.join(part.split()))])
        # Insert <br /> between parts (but not after the last part)
        if i < len(parts) - 1:
            result.append(LeafNode(tag="br", value=""))

    return result


def markdown_to_html_node(markdown: str) -> ParentNode:
    """Convert a markdown string to an HTML ParentNode."""
    blocks = markdown_to_blocks(markdown)
    children: List[HTMLNode] = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            children.append(ParentNode(tag="p", children=parse_children(block)))

        elif block_type == BlockType.HEADING:
            heading_text = block.lstrip('# ').strip()  # Remove leading '#'s and space
            heading_level = len(block) - len(block.lstrip('#'))  # Count number of '#'s
            children.append(ParentNode(tag=f"h{heading_level}", children=parse_children(heading_text)))

        elif block_type == BlockType.CODE:
            # Extract code content (skip first line with ``` and optional language)
            first_newline = block.find('\n')
            code_content = block[first_newline + 1 : -3]
            children.append(ParentNode(tag="pre", children=[
                            ParentNode(tag="code", children=[
                            text_node_to_html_node(TextNode(code_content, TextType.TEXT))])]))

        elif block_type == BlockType.QUOTE:
            quote_text = '\n'.join(
                line[2:] if line.startswith('> ') else line[1:]
                for line in block.splitlines()
            )
            children.append(ParentNode(tag="blockquote", children=parse_children(quote_text)))

        elif block_type == BlockType.UNORDERED_LIST:
            list_items = [line[2:] for line in block.splitlines()]  # Skip "- ", "* ", or "+ "
            children.append(ParentNode(tag="ul", children=[
                            ParentNode(tag="li", children=parse_children(item)) for item in list_items]))
            
        elif block_type == BlockType.ORDERED_LIST:
            list_items = [line.split('. ', 1)[1].strip() for line in block.splitlines()]
            children.append(ParentNode(tag="ol", children=[
                            ParentNode(tag="li", children=parse_children(item)) for item in list_items]))
        
        elif block_type == BlockType.HORIZONTAL_RULE:
            children.append(LeafNode(tag="hr", value=""))
            
    return ParentNode(tag="div", children=children)

