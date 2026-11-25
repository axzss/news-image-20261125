#!/usr/bin/env python3
"""Copy the bundled front-page image to the grader's output directory.

Stdlib only, no network. Deterministic: the same bundled bytes are
written on every run, so two runs produce byte-identical files. The
bundled file is checked to be a PNG before it is copied.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    with open(SRC, "rb") as fh:
        magic = fh.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        raise SystemExit("bundled entry.png is not a PNG file")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
