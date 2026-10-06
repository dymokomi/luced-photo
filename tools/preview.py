#!/usr/bin/env python3
"""Capture a real Metal frame of the window as a PNG.

    tools/preview.py --library DIR [--position N] [--cell POINTS] [--output build/preview.png]

DIR is a library bundle. Uses luce-gpu's
test observer to read the drawable back; no screen access is needed."""
from pathlib import Path
import argparse, os, shutil, struct, subprocess, tempfile, zlib

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--library", type=Path, required=True)
parser.add_argument("--position", type=int, default=0)
parser.add_argument("--cell", type=float, default=0.0)
parser.add_argument("--develop", default="", help="develop settings text to show, e.g. exposure=1;contrast=30")
parser.add_argument("--guides", action="store_true", help="show the guide tool")
parser.add_argument("--expanded", action="store_true", help="open every Properties section")
parser.add_argument("--color", action="store_true", help="open the color sections only")
parser.add_argument("--zoom", action="store_true", help="show the photo at 1:1")
parser.add_argument("--export", default="", help="export the photo at --position and the next to this path (JPEG, 2048 px)")
parser.add_argument("--output", type=Path, default=ROOT / "build/preview.png")
arguments = parser.parse_args()


def chunk(tag, payload):
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff)


with tempfile.TemporaryDirectory(prefix="luced-photo-preview-") as temporary:
    project = Path(temporary)
    shutil.copytree(ROOT / "src", project / "src")
    shutil.copy2(ROOT / "tools/preview.luc", project / "src/main.luc")
    native = (ROOT.parent / "luce-gpu/tests/programs/gpu/native.lucb").read_text()
    (project / "src/probe.lucb").write_text(native + "\n" + (ROOT / "tools/readback.lucb").read_text())
    manifest = (ROOT / "package.prisma").read_text()
    for name in [line.split('"')[1] for line in manifest.splitlines() if line.strip().startswith("def dependency")]:
        manifest = manifest.replace(f'"../{name}"', f'"{ROOT.parent / name}"')
    (project / "package.prisma").write_text(manifest)
    binary = project / "preview"
    environment = dict(os.environ, LUCE_CACHE=str(ROOT / "build/cache"))
    subprocess.run([os.environ.get("LUCE", str(ROOT.parent / "luce/build/luce")), "build", str(project / "src/main.luc"), "--native", "-o", str(binary)], check=True, env=environment, timeout=600)
    ppm = project / "preview.ppm"
    subprocess.run([str(binary), str(ppm), str(arguments.library.resolve()), str(arguments.position), str(arguments.cell), arguments.develop, "guides" if arguments.guides else ("expanded" if arguments.expanded else ("color" if arguments.color else ("zoom" if arguments.zoom else ("export" if arguments.export else ""))))] + ([str(Path(arguments.export).resolve())] if arguments.export else []), check=True, timeout=120)
    header, dimensions, maximum, pixels = ppm.read_bytes().split(b"\n", 3)
    width, height = map(int, dimensions.split())
    rows = b"".join(b"\0" + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_bytes(png)
    print(f"{arguments.output} ({width} × {height})")
