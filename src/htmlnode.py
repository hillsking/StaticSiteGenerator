from typing import Optional, List, Dict
from textnode import TextNode, TextType


class HTMLNode:
    """Base class representing an HTML node."""
    def __init__(self, tag: Optional[str] = None, 
                 value: Optional[str] = None,
                 children: Optional[List["HTMLNode"]] = None,
                 props: Optional[Dict[str, str]] = None) -> None:
        
        self.tag = tag              #  HTML tag name (e.g. "p", "a", "h1", etc.)
        self.value = value          #  Value of the HTML tag (e.g. the text inside a paragraph)
        self.children = children    #  Lower level HTMLNode children
        self.props = props          #  Attributes of the HTML tag

    def __repr__(self) -> str:
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"

    def to_html(self) -> str:
        raise NotImplementedError("to_html method must be implemented by subclasses")
    
    def props_to_html(self) -> str:
        return ('' if not self.props else ''.join(f' {key}="{value}"' for key, value in self.props.items()))


class LeafNode(HTMLNode):
    """Class representing an HTML node that does not have children."""
    def __init__(self, tag: Optional[str], value: str,
                 props: Optional[Dict[str, str]] = None) -> None:
        super().__init__(tag=tag, value=value, children=None, props=props)
    
    def __repr__(self) -> str:
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"
    
    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("LeafNode must have a value to convert to HTML")
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>" if self.tag else self.value


class ParentNode(HTMLNode):
    """Class representing an HTML node that have children."""
    def __init__(self, tag: str, children: List["HTMLNode"],
                 props: Optional[Dict[str, str]] = None) -> None:
        super().__init__(tag=tag, value=None, children=children, props=props)

    def __repr__(self) -> str:
        return f"ParentNode(tag={self.tag}, children={self.children}, props={self.props})"
    
    def to_html(self) -> str:
        if self.tag is None:
            raise ValueError("ParentNode must have a tag to convert to HTML")
        if self.children is None:
            raise ValueError("ParentNode must have children to convert to HTML")
        return (f"<{self.tag}{self.props_to_html()}>"
                f"{''.join(child.to_html() for child in self.children)}"
                f"</{self.tag}>")


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    """Convert a TextNode to an HTML LeafNode."""
    if text_node.text_type == TextType.TEXT:
        return LeafNode(tag=None, value=text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=text_node.text)
    elif text_node.text_type == TextType.LINK:
        if text_node.link is None:
            raise ValueError("Link text type must have a URL")
        return LeafNode(tag="a", value=text_node.text, props={"href": text_node.link})
    elif text_node.text_type == TextType.IMAGE:
        if text_node.link is None:
            raise ValueError("Image text type must have a URL")
        return LeafNode(tag="img", value="", props={"src": text_node.link, "alt": text_node.text})
    
    raise ValueError(f"Unhandled text type: {text_node.text_type}")