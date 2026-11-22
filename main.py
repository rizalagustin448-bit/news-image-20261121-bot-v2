#!/usr/bin/env python3
"""Entry point (stdlib only): copy the pre-rendered entry.png to the output dir."""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"


def main():
    import hashlib

    if not SRC.is_file():
        raise SystemExit(f"missing {SRC}")
    data = SRC.read_bytes()
    if len(data) > 1_048_576:
        raise SystemExit(f"entry.png too big: {len(data)} bytes")
    digest = hashlib.sha256(data).hexdigest()
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    dst = out / "entry.png"
    shutil.copyfile(SRC, dst)
    print("wrote", dst, dst.stat().st_size, "bytes, sha256", digest)


if __name__ == "__main__":
    main()
