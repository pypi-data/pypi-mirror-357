#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Command-line interface for extracting code and text snippets using the llm_text_source library.

Usage:
    cli.py [OPTIONS] PATH_OR_PKGNAME

Options:
    -g, --glob PATTERNS    Glob pattern(s) to match files (default: use library defaults)
    -c, --case-sensitive   Enable case-sensitive glob matching
    -b, --ban PATTERNS     Ban file patterns to exclude
    -p, --parse TYPES      Notebook cell types to include (choices: code, markdown; default: code)
    -e, --encoding ENCODING File encoding (default: utf-8)
    -m, --metadata-only    Only print metadata, not snippets
    -o, --output FILE      Write snippets to a file instead of stdout

"""

import argparse
import sys
from pathlib import Path

from .core import DEFAULT_GLOB_PATTERNS, TextSnippets


def main():
    parser = argparse.ArgumentParser(
        description="Extract and prepare code and text snippets from files or packages for LLM consumption."
    )
    parser.add_argument(
        "path",
        help="File or directory path, or Python package name to extract snippets from.",
    )
    parser.add_argument(
        "-g",
        "--glob",
        nargs="+",
        default=None,
        help=f"Glob pattern(s) to match files (default: {DEFAULT_GLOB_PATTERNS})",
    )
    parser.add_argument(
        "-c",
        "--case-sensitive",
        action="store_true",
        help="Enable case-sensitive glob matching.",
    )
    parser.add_argument(
        "-b",
        "--ban",
        nargs="+",
        help="Ban file patterns to exclude (fnmatch-style patterns).",
    )
    parser.add_argument(
        "-p",
        "--parse",
        nargs="+",
        choices=["code", "markdown"],
        default=["code"],
        help="Notebook cell types to include (choices: code, markdown).",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="File encoding to use (default: utf-8).",
    )
    parser.add_argument(
        "-m",
        "--metadata-only",
        action="store_true",
        help="Only print metadata, not snippet content.",
    )
    parser.add_argument(
        "-o", "--output", help="Write snippet content to a file instead of stdout."
    )
    args = parser.parse_args()

    try:
        snippets = TextSnippets.from_path_or_pkgname(
            path_or_pkgname=args.path,
            glob_patterns=args.glob or DEFAULT_GLOB_PATTERNS,
            case_sensitive=args.case_sensitive,
            ban_file_patterns=args.ban,
            parse_ipynb_cells=args.parse,
            encoding=args.encoding,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Print metadata
    print(snippets.metadata)

    if not args.metadata_only:
        if args.output:
            output_path = Path(args.output)
            try:
                output_path.write_text(snippets.snippets_text, encoding=args.encoding)
                print(f"\nSnippet content written to {output_path}")
            except Exception as e:
                print(f"Error writing to {output_path}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Print snippet content to stdout
            print(snippets.snippets_text)


if __name__ == "__main__":
    main()
