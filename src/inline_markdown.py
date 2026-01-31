import re
from typing import List, Tuple, Optional
from textnode import TextNode, TextType

DELIMETERS = {"**": TextType.BOLD,
              "![": TextType.IMAGE,
              "[": TextType.LINK,
              "_": TextType.ITALIC,
              "`": TextType.CODE}


def get_delimiter(text: str) -> Optional[str]:
    """Args: text - The text to check for delimiters.
       Returns: The first matching delimiter found, or None if none found."""
    for delim in DELIMETERS.keys():
        if text.startswith(delim):
            return delim
    return None


def get_closing_delim_idx(text: str, delim: str) -> Optional[int]:
    """Args: text - The text to search. 
             delim - the opening delimiter.
       Returns: The index of the closing delimiter, or None if not found."""
    if delim not in ("[", "!["):
        idx = text.find(delim)
        return idx if idx != -1 else None

    if ((close_bracket_idx := text.find(']')) == -1 or 
        (close_paren_idx := text.find('(', close_bracket_idx)) == -1):
        return None
        
    depth = 1
    for i, char in enumerate(text[close_paren_idx+1:], close_paren_idx+1):
        depth += (char == '(') - (char == ')')
        if depth == 0:
            return i
    return None



def extract_markdown_images(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Args: text - The markdown text starting with ![.
       Returns: A tuple (alt_text, url) or (None, None) if not found."""
    match = re.match(r'!\[([^\[\]]*)\]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)
    return (match.group(1), match.group(2)) if match else (None, None)


def extract_markdown_links(text: str) -> Tuple[Optional[str], Optional[str]]:    
    """Args: text - The markdown text starting with [.
       Returns: A tuple (link_text, url) or (None, None) if not found."""
    match = re.match(r'\[([^\[\]]*)\]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)
    return (match.group(1), match.group(2)) if match else (None, None)


def get_content_and_link(text: str, delim: str) -> Tuple[Optional[str], Optional[str]]:
    """Args: text - full delimited text (e.g., '**bold**' or '[text](url)').
       Returns: (content, link) tuple."""
    return (extract_markdown_images(text) if delim == "![" else
            extract_markdown_links(text) if delim == "[" else
            (text[len(delim):-len(delim)], None))


def find_first_match(text: str) -> Tuple[str, int, int, Optional[str], Optional[str]] | None:
    """Find first valid delimiter match in text.
       Returns: (delim, start_idx, end_idx, content, link) or None if no match."""
    for start_idx in range(len(text)):
        if (delim := get_delimiter(text[start_idx:])) is None:
            continue  # No delimiter at this position
        
        if (relative_end_idx := get_closing_delim_idx(text[start_idx + len(delim):], delim)) is None:
            continue  # No closing delimiter found
        
        end_idx = (start_idx + len(delim) + relative_end_idx + 1 if delim in ("[", "![") else
                   start_idx + len(delim) + relative_end_idx + len(delim))
        
        content, link = get_content_and_link(text[start_idx:end_idx], delim)
        if not content and not link:
            continue  # Nothing between delimiters
        
        return (delim, start_idx, end_idx, content, link)
    
    return None


def build_text_node(delim: str, content: Optional[str], link: Optional[str], 
                         children: Optional[List[TextNode]]) -> TextNode:
    """Build a TextNode with proper nesting handling.
        Args: delim - delimiter used.
              content - content inside the delimiters.
              link - link URL if applicable.
              children - nested TextNodes if any.
        Returns: TextNode representing the formatted text."""
    has_nesting = (children is not None and (len(children) > 1 or 
                  (len(children) == 1 and children[0].text_type != TextType.TEXT)))
    
    return (TextNode(text='', text_type=DELIMETERS[delim], link=link, children=children) if has_nesting else
            TextNode(text=content, text_type=DELIMETERS[delim], link=link) if content is not None else
            TextNode(text='', text_type=DELIMETERS[delim], link=link))


def text_to_textnodes(text: str) -> List[TextNode]:
    """Convert text with inline markdown to a list of TextNodes.
        Args: text - markdown text to convert.
        Returns: list of TextNodes."""
    if not text:
        return []
    
    if (match := find_first_match(text)) is None:
        return [TextNode(text, TextType.TEXT)]
    
    delim, start, end, content, link = match
    children = text_to_textnodes(content) if (delim != "`") and (content is not None) else None
    
    # Return [TextNode before match] + [Formatted TextNode with children] + [Recursivly build rest]
    return (([TextNode(text[:start], TextType.TEXT)] if start > 0 else []) +
            [build_text_node(delim, content, link, children)] +
            text_to_textnodes(text[end:]))