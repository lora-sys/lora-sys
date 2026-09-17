"""Assemble the four approved generated project covers from temporary base64 chunks.

This helper is intentionally one-shot. The workflow that runs it removes the
helper and staging chunks after the resulting WebP files are verified and
committed.
"""
from __future__ import annotations

import base64
import re
import shutil
from pathlib import Path

from PIL import Image, ImageFile

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "assets/readme/project-covers/staging"
OUT = ROOT / "assets/readme/project-covers"
BUILD = ROOT / "scripts/build_approved_profile.py"

ImageFile.LOAD_TRUNCATED_IMAGES = True

NAMES = ("arena", "skills", "vllm", "vision")
REMOTE_LINES = {
    "arena": "  'arena':'https://raw.githubusercontent.com/lora-sys/AgentArena/main/docs/qa/visual-baselines/v052-home-desktop-20260725.png',",
    "skills": "  'skills':'https://raw.githubusercontent.com/lora-sys/skills/main/assets/readme/hero.png',",
    "vllm": "  'vllm':'https://raw.githubusercontent.com/lora-sys/nano-vllm-interactive-guide/main/assets/readme/hero-v1.webp',",
    "vision": "  'vision':'https://raw.githubusercontent.com/lora-sys/free-vision-skill/main/assets/readme/hero-v1.webp',",
}


def decode_cover(name: str) -> None:
    folder = STAGING / name
    chunks = sorted(folder.glob("*.b64"))
    if not chunks:
        raise RuntimeError(f"No staging chunks for {name}")
    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in chunks)
    if not re.fullmatch(r"[A-Za-z0-9+/=]+", encoded):
        raise RuntimeError(f"Invalid base64 alphabet in {name}")
    encoded += "=" * ((4 - len(encoded) % 4) % 4)
    raw = base64.b64decode(encoded, validate=False)
    temp = OUT / f".{name}.source.webp"
    temp.write_bytes(raw)
    try:
        with Image.open(temp) as image:
            image.load()
            if image.size != (640, 280):
                raise RuntimeError(f"Unexpected {name} size: {image.size}")
            rgb = image.convert("RGB")
            target = OUT / f"{name}.webp"
            rgb.save(target, "WEBP", quality=92, method=6)
            with Image.open(target) as check:
                check.load()
                if check.size != (640, 280):
                    raise RuntimeError(f"Saved {name} size changed: {check.size}")
    finally:
        temp.unlink(missing_ok=True)


def patch_build_sources() -> None:
    source = BUILD.read_text(encoding="utf-8")
    for name, remote in REMOTE_LINES.items():
        local = f"  '{name}':ROOT/'assets/readme/project-covers/{name}.webp',"
        if local in source:
            continue
        if remote not in source:
            raise RuntimeError(f"Expected old source line missing for {name}")
        source = source.replace(remote, local, 1)
    BUILD.write_text(source, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        decode_cover(name)
    patch_build_sources()
    # Remove the accidental placeholder from the earlier interrupted upload.
    (OUT / "arena.webp.b64").unlink(missing_ok=True)
    # Staging chunks are no longer needed once verified WebPs exist.
    shutil.rmtree(STAGING, ignore_errors=True)
    print("Assembled and verified:", ", ".join(NAMES))


if __name__ == "__main__":
    main()
