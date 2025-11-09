"""CSS and HTML cleaning utilities for text preprocessing."""

import re


def strip_html_keep_text(html: str) -> str:
    """
    Extract plain text from HTML by removing all tags.

    Args:
        html: Input HTML string.

    Returns:
        Plain text with tags removed and whitespace normalized.
    """
    # Remove script tags and their contents
    html = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html, flags=re.IGNORECASE)

    # Remove all remaining HTML tags
    html = re.sub(r"<[^>]+>", "", html)

    # Normalize whitespace: convert \r to \n, collapse blank lines
    html = re.sub(r"\r", "\n", html)
    html = re.sub(r"\n[ \t]+\n", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def remove_css_blocks(text: str) -> str:
    """
    Remove CSS blocks (selector { ... }) from text.

    Args:
        text: Input text potentially containing CSS.

    Returns:
        Text with CSS blocks removed.
    """
    # Remove at-rules (@media, @keyframes, etc.) first
    text = remove_at_rule_blocks(text)

    # Remove simple CSS blocks (no nested braces)
    simple_block_pattern = re.compile(
        r"""
        [^\{\};]+      # selector part
        \{             # opening brace
        [^\{\}]*       # content without nested braces
        \}             # closing brace
        """,
        re.VERBOSE,
    )

    # Iterate until no more blocks are found
    prev = None
    while prev != text:
        prev = text
        text = re.sub(simple_block_pattern, "", text)

    return text


def remove_at_rule_blocks(text: str) -> str:
    """
    Remove CSS at-rule blocks (@media, @keyframes, etc.) using brace matching.

    Args:
        text: Input text containing CSS at-rules.

    Returns:
        Text with at-rule blocks removed.
    """
    result = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == "@":
            # Find opening brace
            brace_start = text.find("{", i)
            if brace_start == -1:
                # No brace found, keep character
                result.append(text[i])
                i += 1
                continue

            # Match braces to find closing brace at same depth
            depth = 0
            j = brace_start
            matched = False
            while j < n:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        matched = True
                        break
                j += 1

            if matched:
                # Skip entire at-rule block
                i = j + 1
                continue
            else:
                # Malformed block, keep character
                result.append(text[i])
                i += 1
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def remove_all_css(text: str) -> str:
    """
    Remove all CSS from text (style tags, links, inline attributes, code blocks).

    Args:
        text: Input text containing CSS.

    Returns:
        Text with all CSS removed and whitespace normalized.
    """
    # Remove <style> blocks
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", text, flags=re.IGNORECASE)

    # Remove stylesheet link tags
    text = re.sub(
        r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', "", text, flags=re.IGNORECASE
    )

    # Remove inline style attributes (handles both single and double quotes)
    text = re.sub(r'\sstyle\s*=\s*"[^"]*"', "", text, flags=re.IGNORECASE)
    text = re.sub(r"\sstyle\s*=\s*'[^']*'", "", text, flags=re.IGNORECASE)

    # Remove raw CSS code blocks
    text = remove_css_blocks(text)

    # Normalize whitespace
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = text.strip()

    return text
