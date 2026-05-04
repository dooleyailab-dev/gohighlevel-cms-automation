#!/usr/bin/env python3
"""
GoHighLevel CMS Automation Tool
Convert Markdown files to HTML and wrap in master template frame.
Automatically strips ' - Copy' from titles and headers.
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Error: markdown library not installed.")
    print("Install with: pip install markdown")
    sys.exit(1)


def strip_copy_suffix(text):
    """
    Remove ' - Copy' suffix from text (case-insensitive).
    
    Args:
        text (str): Input text to clean
        
    Returns:
        str: Text with ' - Copy' removed
    """
    return re.sub(r'\s*-\s*Copy\s*$', '', text, flags=re.IGNORECASE)


def extract_title_from_html(html_content):
    """
    Extract and clean the H1 title from HTML content.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        str: Cleaned title without ' - Copy' suffix
    """
    # Match <h1>...</h1> pattern
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE)
    if h1_match:
        title_text = h1_match.group(1)
        # Remove any HTML tags from title
        title_text = re.sub(r'<[^>]+>', '', title_text)
        return strip_copy_suffix(title_text.strip())
    return "Untitled"


def clean_headers_in_html(html_content):
    """
    Remove ' - Copy' suffix from all heading tags (h1-h6).
    
    Args:
        html_content (str): HTML content
        
    Returns:
        str: HTML with cleaned headers
    """
    def replace_header(match):
        tag_open = match.group(1)  # <h1>, <h2>, etc.
        header_content = match.group(2)  # Content between tags
        tag_close = match.group(3)  # </h1>, </h2>, etc.
        
        # Remove HTML tags from content first
        clean_text = re.sub(r'<[^>]+>', '', header_content)
        # Strip the ' - Copy' suffix
        clean_text = strip_copy_suffix(clean_text)
        
        return f"{tag_open}{clean_text}{tag_close}"
    
    # Match all header tags (h1-h6) with content
    cleaned = re.sub(
        r'(<h[1-6][^>]*>)(.*?)(</h[1-6]>)',
        replace_header,
        html_content,
        flags=re.IGNORECASE | re.DOTALL
    )
    return cleaned


def markdown_to_html(markdown_file_path):
    """
    Convert Markdown file to HTML.
    
    Args:
        markdown_file_path (str): Path to markdown file
        
    Returns:
        str: Generated HTML content
        
    Raises:
        FileNotFoundError: If markdown file doesn't exist
    """
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"Markdown file not found: {markdown_file_path}")
    
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        markdown_content,
        extensions=['tables', 'fenced_code', 'codehilite']
    )
    
    return html_content


def load_template(template_path):
    """
    Load the master frame template.
    
    Args:
        template_path (str): Path to template file
        
    Returns:
        str: Template content
        
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_html_post(markdown_file, template_file, output_file=None, verbose=False):
    """
    Generate HTML post by combining markdown content with template frame.
    
    Args:
        markdown_file (str): Path to markdown file
        template_file (str): Path to template file
        output_file (str): Output file path (optional, derived from markdown file if not provided)
        verbose (bool): Enable verbose output
        
    Returns:
        tuple: (output_path, title)
    """
    if verbose:
        print(f"📖 Reading markdown file: {markdown_file}")
    
    # Convert markdown to HTML
    blog_html = markdown_to_html(markdown_file)
    
    if verbose:
        print(f"✨ Markdown converted to HTML ({len(blog_html)} characters)")
    
    # Extract title from H1
    title = extract_title_from_html(blog_html)
    if verbose:
        print(f"📝 Extracted title: '{title}'")
    
    # Clean ' - Copy' from all headers
    blog_html = clean_headers_in_html(blog_html)
    if verbose:
        print(f"🧹 Cleaned headers - removed ' - Copy' suffix")
    
    # Load template
    if verbose:
        print(f"📄 Loading template: {template_file}")
    template_content = load_template(template_file)
    
    # Replace placeholders
    final_html = template_content.replace('{{BLOG_CONTENT}}', blog_html)
    final_html = final_html.replace('{{TITLE}}', title)
    
    # Determine output file path
    if output_file is None:
        # Use markdown filename with .html extension
        base_name = Path(markdown_file).stem
        output_file = f"{base_name}.html"
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    if verbose:
        print(f"✅ HTML post generated: {output_file}")
        print(f"   Title: '{title}'")
        print(f"   Size: {len(final_html)} characters")
    
    return output_file, title


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert Markdown to HTML wrapped in GoHighLevel CMS template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python3 generate_post.py blog.md
  
  # Specify output file
  python3 generate_post.py blog.md -o output.html
  
  # Use custom template
  python3 generate_post.py blog.md -t /path/to/template.html
  
  # Verbose mode
  python3 generate_post.py blog.md -v
        '''
    )
    
    parser.add_argument(
        'markdown_file',
        help='Path to Markdown file'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output HTML file (default: same name as markdown with .html extension)'
    )
    
    parser.add_argument(
        '-t', '--template',
        default='master_frame.html',
        help='Path to template file (default: master_frame.html)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        output_file, title = generate_html_post(
            args.markdown_file,
            args.template,
            args.output,
            args.verbose
        )
        print(f"\n✅ Success! Generated: {output_file}")
        print(f"   Title: {title}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()