from enum import Enum
from typing import Optional, List

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType = TextType.TEXT, 
                 link: Optional[str] = None,
                 children: Optional[List['TextNode']] = None) -> None:
        self.text = text
        self.text_type = text_type
        self.link = link
        self.children = children

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, TextNode) and
                self.text == other.text and
                self.text_type == other.text_type and
                self.link == other.link and
                self.children == other.children)
    
    def __repr__(self) -> str:
        return ((f"TextNode('{self.text}', {self.text_type}") +
                (f", {self.link})" if self.link else ")") +
                (f", children={self.children})" if self.children else ")"))