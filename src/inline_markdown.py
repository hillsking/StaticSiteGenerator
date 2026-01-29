import re
from typing import List, Tuple
from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes: List[TextNode], 
                          delimiter: str, text_type: TextType) -> List[TextNode]:
    """Args: old_nodes - List of TextNodes to split by delimiter, 
             delimiter - The markdown delimiter to split by (e.g. "**" for bold),
             text_type - The TextType to assign to the split parts.
       Returns: A new list of TextNodes with the specified delimiter split out."""
    
    lst: List[TextNode] = []
    for node in old_nodes:
        # If the node is not plain text or has no delimiter, we keep it as is
        if node.text_type != TextType.TEXT or delimiter not in node.text:
            lst.append(node)
            continue
        
        parts = node.text.split(delimiter)
        # If the delimiter is not found or unmatched, raise an error
        if len(parts) % 2 == 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in text '{node.text}'")
        
        # Otherwise, we split by the delimiter
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Even index: plain text
                if part:
                    lst.append(TextNode(part, TextType.TEXT))
            else:
                # Odd index: formatted text
                if part:
                    lst.append(TextNode(part, text_type))
                else:
                    raise ValueError(f"Empty text between delimiters '{delimiter}' in text '{node.text}'")

    return lst


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    """Args: text - The markdown text to extract images from.
       Returns: A list of tuples containing (alt_text, url) for each image found."""
    return re.findall(r'!\[([^\[\]]*)\]\(([^\(\)]*)\)', text)


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:    
    """Args: text - The markdown text to extract links from.
       Returns: A list of tuples containing (link_text, url) for each link found."""
    return re.findall(r'(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)', text)


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    """Args: old_nodes - List of TextNodes to split by markdown image syntax.
       Returns: A new list of TextNodes with markdown images split out as separate nodes."""
    lst: List[TextNode] = []
    for node in old_nodes:
        # If the node is not plain text or has no image syntax, we keep it as is
        images: List[Tuple[str, str]] = extract_markdown_images(node.text)
        if node.text_type != TextType.TEXT or not images:
            lst.append(node)
            continue
        
        text_str = node.text
        for alt, url in images:
            parts = text_str.split(f"![{alt}]({url})", 1)
            # Add preceding text if any
            if parts[0]:
                lst.append(TextNode(parts[0], TextType.TEXT))
            # Add image node
            lst.append(TextNode(alt, TextType.IMAGE, url))
            # Update the remaining text to process
            text_str = parts[1] if len(parts) > 1 else ''
        # Add any remaining text after the last image
        if text_str:
            lst.append(TextNode(text_str, TextType.TEXT))
    
    return lst


def split_nodes_link(old_nodes: List[TextNode]) -> List[TextNode]:
    """Args: old_nodes - List of TextNodes to split by markdown link syntax.
       Returns: A new list of TextNodes with markdown links split out as separate nodes."""
    lst: List[TextNode] = []
    for node in old_nodes:
        # If the node is not plain text or has no link syntax, we keep it as is
        links: List[Tuple[str, str]] = extract_markdown_links(node.text)
        if node.text_type != TextType.TEXT or not links:
            lst.append(node)
            continue
        
        text_str = node.text
        for link_text, url in links:
            parts = text_str.split(f"[{link_text}]({url})", 1)
            # Add preceding text if any
            if parts[0]:
                lst.append(TextNode(parts[0], TextType.TEXT))
            # Add link node
            lst.append(TextNode(link_text, TextType.LINK, url))
            # Update the remaining text to process
            text_str = parts[1] if len(parts) > 1 else ''
        # Add any remaining text after the last link
        if text_str:
            lst.append(TextNode(text_str, TextType.TEXT))
    
    return lst


def text_to_textnodes(text: str) -> List[TextNode]:
    """Args: text - The plain text to convert.
       Returns: A list of text nodes with all text_types in original text in order."""
    if not text:
        return []
    nodes = [TextNode(text, TextType.TEXT)]  # Initial node with all text
    
    # Process delimiters in order
    for delimiter, text_type in [("**", TextType.BOLD), ("_", TextType.ITALIC), ("`", TextType.CODE)]:
        nodes = split_nodes_delimiter(nodes, delimiter, text_type)
    
    # Process links and images
    return split_nodes_link(split_nodes_image(nodes))