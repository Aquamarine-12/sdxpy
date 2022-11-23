"""Ivy configuration file."""

# Abbreviation for this document.
abbrev = "sdxpy"

# GitHub repository.
repo = "https://github.com/gvwilson/sdpy"

# Site settings.
lang = "en"
title = "Software Design in Python"
acronym = "SDPy"
tagline = "a tool-based introduction"
author = "Greg Wilson"
email = "gvwilson@third-bit.com"
plausible = "third-bit.com"
archive = f"{abbrev}-examples.zip"

# Chapters.
chapters = [
    "introduction",
    "tester",
    "interpreter",
    "backup",
    "persistence",
    "binary",
    "builder",
    "templating",
    "layout",
    "server",
    "matching",
    "parser",
    "linter",
    "vm",
    "debugger",
    "dataframe",
    "pipeline",
    "cache",
    "database",
    "packman",
    "conclusion",
]

# Appendices (slugs in order).
appendices = [
    "bibliography",
    "syllabus",
    "license",
    "conduct",
    "contributing",
    "glossary",
    "credits",
    "contents",
]

# To do.
todo = [
    "dataframe",
    "pipeline",
    "cache",
    "database",
    "packman",
]

# Files to copy verbatim.
copy = [
    "*.ht",
]

# Exclusions (don't process).
exclude = [
    "*.as",
    "*.ht",
    "*.mx",
    "*.tll",
]

# Debug.
debug = True

# Warn about missing or unused entries.
warnings = True

# ----------------------------------------------------------------------

# Theme.
theme = "mccole"

# Enable various Markdown extensions.
markdown_settings = {
    "extensions": [
        "markdown.extensions.extra",
        "markdown.extensions.smarty",
        "pymdownx.superfences",
    ]
}

# External files.
acknowledgments = "info/acknowledgments.yml"
bibliography = "info/bibliography.bib"
bibliography_style = "unsrt"
credits = "info/credits.yml"
glossary = "info/glossary.yml"
links = "info/links.yml"
dom = "info/dom.yml"

# Input and output directories.
src_dir = "src"
out_dir = "docs"

# Use "a/" URLs instead of "a.html".
extension = "/"

# Files to copy verbatim.
copy += [
    "*.jpg",
    "*.js",
    "*.json",
    "*.out",
    "*.png",
    "*.py",
    "*.sh",
    "*.svg",
    "*.txt",
    "*.yml",
]

# Exclusions (don't process).
exclude += [
    "Makefile",
    "*.csv",
    "*.ht",
    "*.jpg",
    "*.js",
    "*.json",
    "*.mk",
    "*.out",
    "*.pdf",
    "*.png",
    "*.py",
    "*.pyc",
    "*.sh",
    "*.svg",
    "*.txt",
    "*.yml",
    "*~",
    "__pycache__",
    ".pytest_cache",
]

# ----------------------------------------------------------------------

# Display values for LaTeX generation.
if __name__ == "__main__":
    import sys
    assert len(sys.argv) == 2, "Expect exactly one argument"
    if sys.argv[1] == "--abbrev":
        print(abbrev)
    elif sys.argv[1] == "--latex":
        print(f"\\title{{{title}}}")
        print(f"\\subtitle{{{tagline}}}")
        print(f"\\author{{{author}}}")
    elif sys.argv[1] == "--tagline":
        print(tagline)
    elif sys.argv[1] == "--title":
        print(title)
    else:
        assert False, f"Unknown flag {sys.argv[1]}"
