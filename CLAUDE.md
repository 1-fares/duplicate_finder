# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Command-line tool that finds duplicate files by comparing SHA-256 hashes of file contents. Uses uv for project management. A legacy Python 2 version (`duplicate_finder_python2.py`) also exists.

## Usage

```bash
# Via uv
uv run duplicate_finder.py <directory_path>

# Via shell script
./run.sh <directory_path>

# As installed entry point
uv run duplicate-finder <directory_path>
```

Requires Python >=3.13. No third-party dependencies (stdlib only: `argparse`, `hashlib`, `pathlib`).

## Architecture

Single-script tool (`duplicate_finder.py`) with a `main()` entry point registered in `pyproject.toml`.

- Files are read in 16MB chunks (`read_in_chunks` generator) to handle large files without loading them entirely into memory
- Duplicates are identified by grouping files with the same SHA-256 hash + file size as a composite key
- Progress indicators go to stderr (`O` per file, `.` per chunk beyond the first), results go to stdout
- Zero-byte files are skipped
- Uses `Path.rglob` for recursive directory traversal and `argparse` for CLI argument handling
