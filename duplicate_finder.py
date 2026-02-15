import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

PARTIAL_HASH_SIZE = 64 * 1024  # 64KB for partial hash comparison

def _new_hash():
    return hashlib.blake2b(digest_size=16)


def partial_hash(filepath: Path) -> str:
    h = _new_hash()
    with filepath.open("rb") as f:
        h.update(f.read(PARTIAL_HASH_SIZE))
    return h.hexdigest()


def full_hash(filepath: Path) -> str:
    with filepath.open("rb") as f:
        h = hashlib.file_digest(f, _new_hash)
    return h.hexdigest()


def find_duplicates(directory: Path):
    size_groups: dict[int, list[Path]] = defaultdict(list)
    filecount = 0
    skipped = 0

    # Phase 1: group by file size
    for filepath in directory.rglob("*"):
        if filepath.is_symlink() or not filepath.is_file():
            continue
        filecount += 1
        sys.stderr.write("O")
        sys.stderr.flush()
        try:
            size = filepath.stat().st_size
        except OSError as e:
            print(f"\n{filepath.name} {type(e).__name__}: {e}")
            skipped += 1
            continue
        if size == 0:
            continue
        size_groups[size].append(filepath)

    # Phase 2: partial hash for size-matched files
    partial_groups: dict[str, list[Path]] = defaultdict(list)
    for size, paths in size_groups.items():
        if len(paths) < 2:
            continue
        for filepath in paths:
            try:
                h = partial_hash(filepath)
            except OSError as e:
                print(f"\n{filepath.name} {type(e).__name__}: {e}")
                skipped += 1
                continue
            partial_groups[f"{size}_{h}"].append(filepath)

    # Phase 3: full hash for partial-hash-matched files
    full_groups: dict[str, list[Path]] = defaultdict(list)
    for key, paths in partial_groups.items():
        if len(paths) < 2:
            continue
        for filepath in paths:
            sys.stderr.write(".")
            sys.stderr.flush()
            try:
                h = full_hash(filepath)
            except OSError as e:
                print(f"\n{filepath.name} {type(e).__name__}: {e}")
                skipped += 1
                continue
            full_groups[h].append(filepath)

    # Report results
    if filecount > 0:
        print()
    print(f"{filecount} file(s) examined", end="")
    if skipped:
        print(f" ({skipped} skipped due to errors)", end="")
    print()

    found = False
    for file_hash, dupes in full_groups.items():
        if len(dupes) < 2:
            continue
        found = True
        print(f"{len(dupes)} duplicates with hash {file_hash}:")
        for filepath in dupes:
            print(f"  {filepath}")
        print()

    if filecount > 1 and not found:
        print("No duplicates found")


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files by content")
    parser.add_argument("path", type=Path, help="Directory to scan for duplicates")
    args = parser.parse_args()

    if not args.path.is_dir():
        parser.error(f"Not a valid directory: {args.path}")

    print(f"Scanning {args.path} ...")
    find_duplicates(args.path)


if __name__ == "__main__":
    main()
