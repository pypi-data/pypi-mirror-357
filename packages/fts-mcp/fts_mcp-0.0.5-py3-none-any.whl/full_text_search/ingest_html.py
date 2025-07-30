import re
from typing import Callable

from markdownify import markdownify


def remove_links(md: str) -> tuple[str, dict[str, str]]:
    """Remove link URLs from markdown, returning cleaned markdown and a mapping of link text to URLs."""
    link_mapping = {}

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        link_mapping[link_text] = link_url
        return f"[{link_text}]()"

    # Match markdown links: [text](url)
    cleaned_md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, md)

    return cleaned_md, link_mapping


def replace_links(md: str, link_mapping: dict[str, str]) -> str:
    """Replace empty link URLs with the original URLs from the mapping."""

    def restore_link(match):
        link_text = match.group(1)
        if link_text in link_mapping:
            return f"[{link_text}]({link_mapping[link_text]})"
        return match.group(0)  # Return original if no mapping found

    # Match markdown links with empty URLs: [text]()
    return re.sub(r"\[([^\]]+)\]\(\)", restore_link, md)


def remove_attributes(html_string: str):
    def remove_attrs(match):
        tag_name = match.group(1)
        return f"<{tag_name}>"

    pattern = r"<([^>\s]+)[^>]*>"
    return re.sub(pattern, remove_attrs, html_string)


def remove_lines(md: str, predicate: Callable[[str], bool]):
    """predicate identifies lines to REMOVE"""
    lines = md.splitlines()

    lines = [line for line in lines if not predicate(line)]

    return "\n".join(lines)


def html_to_markdown(html_string: str):
    md = markdownify(html_string)

    # the replace stuff we don't want
    if "Back To TOC" in md:
        md = md.split("Back To TOC")[1]

    md = remove_lines(md, lambda line: line.startswith("Select Language"))
    md = remove_lines(
        md, lambda line: line.startswith("Powered by [![Google Translate]")
    )

    md = md.replace("![]()", "")

    md = md.replace("\n---\n", "\n")

    md = re.sub(r"\n{3,}", "\n\n", md)

    return md


PROMPT = (
    "Below is some Markdown/text saved from a webpage. "
    "Make your best attempt at removing any boilerplate, leaving only the text "
    "that you think is the main content area. Boilerplate includes navigation menus, "
    "copyright notices, privacy policy links, stuff like that. Everything but the main content. "
    "If there doesn't appear to be any main content or the page is empty / all boilerplace, "
    "you may return an empty string. Do not add any prelude or commentary, just return the cleaned page. "
    "IMPORTANT: Preserve all links in the format [text]() even if the parentheses are empty - the URLs "
    "have been removed to save tokens and will be restored later.\n\n"
)


async def remove_boilerplate(markdown: str):
    from lm_deluge import LLMClient

    markdown, mapping = remove_links(markdown)
    client = LLMClient(max_new_tokens=10_000)
    res = await client.process_prompts_async([PROMPT + markdown], show_progress=False)

    return replace_links(res[0].completion, mapping)  # type: ignore


async def remove_boilerplate_batch(markdown: list[str]):
    from lm_deluge import LLMClient

    # Remove links from all documents and collect mappings
    cleaned_docs_and_mappings = [remove_links(md) for md in markdown]
    cleaned_docs, mappings = zip(*cleaned_docs_and_mappings)

    client = LLMClient(
        max_requests_per_minute=1_000,
        max_tokens_per_minute=1_000_000,
        max_new_tokens=10_000,
        request_timeout=75,
    )
    res = await client.process_prompts_async([(PROMPT + x) for x in cleaned_docs])

    # Restore links using the corresponding mappings
    return [replace_links(r.completion, mapping) for r, mapping in zip(res, mappings)]  # type: ignore


async def read_html(html_string: str):
    return await remove_boilerplate(markdownify(html_string))
