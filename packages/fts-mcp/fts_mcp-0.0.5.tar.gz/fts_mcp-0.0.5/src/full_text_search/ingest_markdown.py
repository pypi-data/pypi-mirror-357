#!/usr/bin/env python3
"""
Utilities for turning Markdown (e.g. PDF-to-Markdown output) into JSONL chunks for RAG.

Core steps
----------
1. Optionally strip Markdown image links.
2. Split on every header line (`#`, `##`, …) so each header starts a new chunk.
3. Merge “tiny” chunks (default < 500 chars) into the *following* chunk.
4. Write one JSONL object per chunk under the key `"text"`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List

# ---------- regexes ---------------------------------------------------------

_IMG = re.compile(r"!\[[^\]]*]\([^)]*\)")  # ![alt](url)
_HDR = re.compile(r"^\s*#{1,6}\s")  # lines starting with 1-6 “# ”

# ---------- basic transforms -----------------------------------------------


def remove_image_links(md: str) -> str:
    """Strip every Markdown image link."""
    return _IMG.sub("", md)


def split_into_chunks(md: str) -> List[str]:
    """
    Split so that *each* Markdown header begins a new chunk.
    The header line itself stays with the chunk it starts.
    """
    lines = md.splitlines()
    out: List[str] = []
    cur: List[str] = []

    for line in lines:
        if _HDR.match(line) and cur:
            out.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)

    if cur:
        out.append("\n".join(cur).strip())

    return [c for c in out if c]  # drop empties


def coalesce_small_chunks(chunks: List[str], min_size: int = 500) -> List[str]:
    """
    Merge any chunk shorter than *min_size* into the *following* chunk.
    (If it’s the last chunk, it’s left as-is.)
    """
    merged: List[str] = []
    i = 0
    while i < len(chunks):
        chunk = chunks[i]
        if len(chunk) < min_size and i + 1 < len(chunks):
            merged.append(chunk.rstrip() + "\n\n" + chunks[i + 1].lstrip())
            i += 2  # skip what we just merged
        else:
            merged.append(chunk)
            i += 1
    return merged


# ---------- pipeline & file helpers ----------------------------------------


def process(md: str, *, remove_images: bool = True, min_size: int = 500) -> List[str]:
    """Run the full pipeline and return the final chunks."""
    if remove_images:
        md = remove_image_links(md)
    chunks = split_into_chunks(md)
    return coalesce_small_chunks(chunks, min_size=min_size)


def markdown_to_jsonl(
    src: Path,
    dst: Path,
    *,
    remove_images: bool = True,
    min_size: int = 500,
) -> None:
    """Convert *src* Markdown file to JSONL at *dst*."""
    chunks = process(
        src.read_text(encoding="utf-8"), remove_images=remove_images, min_size=min_size
    )
    with dst.open("w", encoding="utf-8") as fh:
        for c in chunks:
            json.dump({"text": c}, fh, ensure_ascii=False)
            fh.write("\n")


# ---------- CLI ------------------------------------------------------------


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Ingest Markdown and output JSONL chunks.")
    ap.add_argument("input_md", type=Path, help="Source Markdown file")
    ap.add_argument("output_jsonl", type=Path, help="Destination JSONL file")
    ap.add_argument(
        "--keep-images", action="store_true", help="Do NOT strip image links"
    )
    ap.add_argument(
        "--min-size", type=int, default=500, help="Minimum chunk size in characters"
    )
    args = ap.parse_args()

    markdown_to_jsonl(
        args.input_md,
        args.output_jsonl,
        remove_images=not args.keep_images,
        min_size=args.min_size,
    )


if __name__ == "__main__":
    _cli()
