import re


def strip_html_keep_text(html: str) -> str:
    """
    Very simple HTML -> text extractor:
    - removes all tags like <...>
    - collapses multiple blank lines
    This avoids external libraries.
    """
    # remove script contents
    html = re.sub(r"<script[^>]*>[\s\S]*?</script>", "", html, flags=re.IGNORECASE)

    # remove remaining tags completely
    html = re.sub(r"<[^>]+>", "", html)

    # collapse whitespace
    html = re.sub(r"\r", "\n", html)
    html = re.sub(r"\n[ \t]+\n", "\n", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def remove_css_blocks(text: str) -> str:
    """
    Remove CSS-like blocks of the form:
    selector { ... }
    including nested-looking content such as @media queries.

    Strategy:
    - Greedy match from a selector up to the matching closing brace at same depth
      is hard with pure regex, so we approximate:
      1. Remove @media/@keyframes blocks with balanced braces using a manual parser.
      2. Then repeatedly remove simple selector { ... } one-level blocks with regex.
    """
    # First: remove at-rule blocks like @media, @supports, @keyframes
    text = remove_at_rule_blocks(text)

    # Then repeatedly remove simple "foo { ... }" blocks with no nested braces
    simple_block_pattern = re.compile(
        r"""
        [^\{\};]+      # selector part (not { or } or ;)
        \{             # opening brace
        [^\{\}]*       # block content without nested braces
        \}             # closing brace
        """,
        re.VERBOSE,
    )

    prev = None
    while prev != text:
        prev = text
        text = re.sub(simple_block_pattern, "", text)

    return text


def remove_at_rule_blocks(text: str) -> str:
    """
    Removes at-rule style blocks like:
    @media (...) { ... }
    @supports ... { ... }
    @keyframes name { ... }
    We do this with a small brace-matching parser.
    """
    result = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == "@":
            # move until first '{'
            brace_start = text.find("{", i)
            if brace_start == -1:
                # no '{', so not actually a block like @media { ... }
                result.append(text[i])
                i += 1
                continue

            # now walk braces to find the matching closing '}' at same depth
            depth = 0
            j = brace_start
            matched = False
            while j < n:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                    if depth == 0:
                        # block ends at j
                        matched = True
                        break
                j += 1

            if matched:
                # We skip the whole @rule block
                i = j + 1
                continue
            else:
                # malformed, fallback to keep char and move on
                result.append(text[i])
                i += 1
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def remove_all_css(text: str) -> str:
    """
    Remove as much CSS as possible from text.
    Steps:
    1. Remove <style>...</style>
    2. Remove <link ... rel="stylesheet" ...>
    3. Remove inline style attributes style="..." or style='...'
    4. Remove CSS code blocks, including @media etc.
    5. Cleanup multiple blank lines
    """

    # 1. Remove <style> blocks (case-insensitive, multiline)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", text, flags=re.IGNORECASE)

    # 2. Remove <link ... rel="stylesheet" ...> tags
    text = re.sub(
        r'<link[^>]*rel=["\']stylesheet["\'][^>]*>', "", text, flags=re.IGNORECASE
    )

    # 3. Remove inline style attributes (double or single quotes)
    #    Examples:
    #    <div style="color:red; font-size:12px">
    #    <p STYLE='margin:0;padding:0'>
    text = re.sub(r'\sstyle\s*=\s*"[^"]*"', "", text, flags=re.IGNORECASE)
    text = re.sub(r"\sstyle\s*=\s*'[^']*'", "", text, flags=re.IGNORECASE)

    # 4. Remove raw CSS-like content outside of tags
    text = remove_css_blocks(text)

    # 5. Collapse excessive blank lines / whitespace
    text = re.sub(r"[ \t]+\n", "\n", text)  # trim line-end spaces
    text = re.sub(r"\n\s*\n+", "\n\n", text)  # collapse many blank lines
    text = text.strip()

    return text
