#!/usr/bin/env bash
set -euo pipefail
exec uv run duplicate_finder.py "$@"
