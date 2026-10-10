"""Prepare a fingerprinted Pages artifact using only Python's standard library."""
import argparse
import hashlib
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

ATTR = re.compile(r"""(\b(?:src|href|poster)\s*=\s*)(["'])(.*?)\2""", re.I)
CSS_URL = re.compile(r"""url\(\s*(["']?)(.*?)\1\s*\)""", re.I)
CSS_IMPORT = re.compile(r"""(@import\s+)(["'])(.*?)\2""", re.I)
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def build(source=ROOT, output=None):
    source = Path(source).resolve()
    output = Path(output or source / "_site").resolve()
    if output == source or source.is_relative_to(output):
        raise ValueError("Output must not contain the source directory")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output must be empty; use a new output directory")
    output.mkdir(parents=True, exist_ok=True)
    paths = [p for p in source.iterdir()
             if p.is_file() and p.suffix.lower() in {".css", ".js", ".vcf"}]
    assets = source / "assets"
    if assets.exists():
        paths.extend(p for p in assets.rglob("*") if p.is_file())
    originals = {}
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError(f"Unsafe asset: {path}")
        originals[path.relative_to(source).as_posix()] = path.read_bytes()
    mapping, hashes, active = {}, {}, set()

    def rewrite(url, owner):
        url = html.unescape(url)
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            return url
        if parts.path.startswith("/"):
            raise ValueError(f"Use relative local paths: {url}")
        key = posixpath.normpath(posixpath.join(
            posixpath.dirname(owner), unquote(parts.path)))
        if key not in originals:
            raise ValueError(f"Missing or unsupported local resource: {owner}: {url}")
        target = emit(key)
        relative = posixpath.relpath(target, posixpath.dirname(owner) or ".")
        return urlunsplit(("", "", quote(relative, safe="/"), parts.query, parts.fragment))

    def emit(key):
        if key in mapping:
            return mapping[key]
        if key in active:
            raise ValueError(f"Circular CSS dependency: {key}")
        active.add(key)
        data = originals[key]
        if key.lower().endswith(".css"):
            text = data.decode("utf-8-sig")
            text = CSS_URL.sub(lambda m: 'url("' + rewrite(m[2], key) + '")', text)
            text = CSS_IMPORT.sub(
                lambda m: m[1] + m[2] + rewrite(m[3], key) + m[2], text)
            data = text.encode("utf-8")
        sha = digest(data)
        path = Path(key)
        target = path.with_name(f"{path.stem}.{sha[:16]}{path.suffix}").as_posix()
        destination = output / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        mapping[key], hashes[target] = target, sha
        active.remove(key)
        return target

    for key in sorted(originals):
        emit(key)
    text = (source / "index.html").read_text(encoding="utf-8-sig")
    text = ATTR.sub(lambda m: m[1] + m[2] +
                    html.escape(rewrite(m[3], "index.html"), quote=True) + m[2], text)
    data = text.encode("utf-8")
    (output / "index.html").write_bytes(data)
    hashes["index.html"] = digest(data)
    (output / ".nojekyll").touch()
    manifest = {"algorithm": "sha256", "assets": mapping, "files": hashes}
    (output / "asset-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Check that preparing the artifact never changed the source assets.
    for key, original in originals.items():
        if (source / key).read_bytes() != original:
            raise RuntimeError(f"Source changed: {key}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.source, args.output)
    print(f"Prepared {len(result['assets'])} versioned resources")
