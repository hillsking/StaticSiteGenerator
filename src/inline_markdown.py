import re
from typing import List, Tuple, Optional
from textnode import TextNode, TextType

DELIMETERS = {"**": TextType.BOLD,
              "__": TextType.BOLD,
              "~~": TextType.STRIKETHROUGH,
              "![": TextType.IMAGE,
              "[": TextType.LINK,
              "_": TextType.ITALIC,
              "*": TextType.ITALIC,
              "`": TextType.CODE}


def get_delimiter(text: str) -> Optional[str]:
    """Args: text - The text to check for delimiters.
       Returns: The first matching delimiter found, or None if none found."""
    for delim in DELIMETERS.keys():
        if text.startswith(delim):
            return delim
    return None


def get_closing_delim_idx(text: str, delim: str) -> Optional[int]:
    """Find closing delimiter index, handling nested brackets for links/images."""
    # Simple case: _, *, ~~, `
    if delim not in ("[", "![", "**", "__"):
        return idx if (idx := text.find(delim)) != -1 else None
    
    # Bold delimiters: ** and __ (handle overlapping like ***)
    if delim in ("**", "__"):
        if (idx := text.find(delim)) == -1:
            return None
        # Check for overlapping: *** has ** at pos 0 and 1
        if idx + 1 < len(text) and text[idx+1:idx+1+len(delim)] == delim:
            after_offset = idx + 1 + len(delim)
            if after_offset >= len(text) or text[after_offset] != delim[0]:
                return idx + 1
        return idx
    
    # Links and images: [ and ![ (handle nesting)
    depth, close_bracket_idx = 0, -1
    for i, char in enumerate(text):
        depth += (char == '[') - (char == ']')
        if depth < 0 and text[i+1:i+2] == '(':
            close_bracket_idx = i
            break
        elif depth < 0:
            depth = 0
    
    if close_bracket_idx == -1:
        return None
    
    paren_depth = 1
    for i, char in enumerate(text[close_bracket_idx+2:], close_bracket_idx+2):
        paren_depth += (char == '(') - (char == ')')
        if paren_depth == 0:
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
    if (match := re.match(r'\[([^\[\]]*)\]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)) is not None:
        return (match.group(1), match.group(2))
    # Handle nested images inside links
    match = re.match(r'\[(!\[[^\[\]]*\]\([^()]*\))\]\(([^()]*(?:\([^()]*\)[^()]*)*)\)', text)
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