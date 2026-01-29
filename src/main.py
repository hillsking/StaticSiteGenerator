import os
import shutil
import sys
from markdown_blocks import markdown_to_html_node


def extract_title(markdown: str) -> str:
    """Extracts the title from the markdown content.
       Args: markdown - The markdown text to extract the title from.
       Returns: The title string."""
    for line in markdown.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    raise Exception("No title found in markdown.")


def copy_static_to_docs(static_dir: str, docs_dir: str) -> None:
    """Copies all files from the static directory to the docs directory."""
    if not os.path.exists(static_dir):
        raise FileNotFoundError(f"Static directory '{static_dir}' does not exist.")
    if os.path.exists(docs_dir):
        shutil.rmtree(docs_dir)
    shutil.copytree(static_dir, docs_dir)


def generate_page(from_path: str, template_path: str, 
                  dest_path: str, basepath: str) -> None:
    """Generates an HTML page from a markdown file using a template."""
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")
    with open(from_path) as md_file:
        markdown_content = md_file.read()

    title = extract_title(markdown_content)
    html_content = markdown_to_html_node(markdown_content).to_html()

    with open(template_path) as template_file:
        template_content = template_file.read()
    final_html = (
        template_content
        .replace("{{ Title }}", title)
        .replace("{{ Content }}", html_content)
        .replace('href="/', f'href="{basepath}')
        .replace('src="/', f'src="{basepath}')
    )

    with open(dest_path, "w") as output_file:
        output_file.write(final_html)


def generate_pages_recursive(dir_path_content: str, template_path: str, 
                             dest_dir_path: str, basepath: str) -> None:
    """Recursively generates HTML pages from markdown files in a directory."""
    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)
        if os.path.isdir(item_path):
            os.makedirs(dest_path, exist_ok=True)
            generate_pages_recursive(item_path, template_path, dest_path, basepath)
        elif item.endswith(".md"):
            dest_file_path = os.path.join(dest_dir_path, item).replace(".md", ".html")
            generate_page(item_path, template_path, dest_file_path, basepath)
 

def main():
    basepath = f"/{sys.argv[1].strip('/')}" if len(sys.argv) > 1 else "/"

    copy_static_to_docs("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

if __name__ == "__main__":
    main()