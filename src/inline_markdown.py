import re
from typing import List, Tuple
from textnode import TextNode, TextType

DELIMETERS = {"**": TextType.BOLD,
              "_": TextType.ITALIC,
              "`": TextType.CODE}


def create_nodes_by_delimiter(text: str) -> List[TextNode]:
    """Args: text - The text to scan recursively.
       Returns: A list of TextNodes split by delimiters."""
    if not text:
        return []
    
    for i in range(len(text)):
        # Check for delimiters at current position
        delim = (text[i] if text[i] in DELIMETERS else
                 text[i:i+2] if len(text) > i+1 and text[i:i+2] in DELIMETERS else None)
        if delim is None:
            continue  # No delimiter at this position - skip
        
        # Find the matching closing delimiter
        start_idx, end_idx = i, text.find(delim, i + len(delim))
        if end_idx == -1:
            continue  # No closing delimiter found - skip
        
        # Extract content between delimiters
        content = text[start_idx + len(delim): end_idx]
        if not content:
            continue  # Empty content between delimiters - skip
        
        # Recursively process content for nested formatting
        children: List[TextNode] = []
        if delim != "`":
            children = create_nodes_by_delimiter(content)

        # Check if content has nested formatting or is plain text
        has_nesting = len(children) > 1 or (len(children) == 1 and children[0].text_type != TextType.TEXT)

        # Return [TEXT before delimiter + delimited content/children + recursively scan after]
        return (([TextNode(text[0:start_idx], TextType.TEXT)] if text[0:start_idx] else []) +
                ([TextNode(text='', text_type=DELIMETERS[delim], children=children)] if has_nesting else
                 [TextNode(text=content, text_type=DELIMETERS[delim])]) +
                 create_nodes_by_delimiter(text[end_idx + len(delim):]))
    
    # No paired delimiters found - return entire text as TEXT node
    return [TextNode(text, TextType.TEXT)]


def split_nodes_delimiter(old_nodes: List[TextNode]) -> List[TextNode]:
    """Args: old_nodes - List of TextNodes to split by delimiter,
       Returns: A new list of TextNodes with the specified delimiter split out."""
    lst: List[TextNode] = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            lst.append(node)
            continue
        lst.extend(create_nodes_by_delimiter(node.text))
    return lst

def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    """Args: text - The markdown text to extract images from.
       Returns: A list of tuples containing (alt_text, url) for each image found."""
    return re.findall(r'!\[([^\[\]]*)]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:    
    """Args: text - The markdown text to extract links from.
       Returns: A list of tuples containing (link_text, url) for each link found."""
    return re.findall(r'(?<!!)\[([^\[\]]*)]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)


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
    return split_nodes_delimiter(split_nodes_link(split_nodes_image([TextNode(text, TextType.TEXT)])))