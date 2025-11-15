#!/usr/bin/env python3
"""
Generate a lightweight repo map for orientation during a Technomancy run.
- Lists directories/files (filtered)
- Extracts top-level classes & functions from Python modules
- Writes runtime/repo_map.md

Usage:
  python tools/generate_repo_map.py --root . --out runtime/repo_map.md \
      --exclude venv,node_modules,.git,dist,build,__pycache__
"""
import os, argparse, ast, sys
from pathlib import Path

DEFAULT_EXCLUDES = {"venv","node_modules",".git","dist","build","__pycache__",".mypy_cache",".pytest_cache",".ruff_cache"}
PY_EXTS = {".py"}

def scan_python_symbols(file_path: Path):
    classes, funcs = [], []
    try:
        src = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
    except Exception as e:
        pass
    return classes, funcs

def should_skip(path: Path, excludes):
    parts = set(path.parts)
    return len(parts.intersection(excludes)) > 0

def build_map(root: Path, excludes):
    outline = []
    for dirpath, dirnames, filenames in os.walk(root):
        p = Path(dirpath)
        if should_skip(p, excludes):
            # prune
            dirnames[:] = [d for d in dirnames if d not in excludes]
            continue
        rel = p.relative_to(root) if p != root else Path(".")
        if rel != Path("."):
            outline.append(f"### {rel.as_posix()}/")
        py_files = []
        other_files = []
        for f in sorted(filenames):
            fp = p/ f
            if f.startswith(".") or should_skip(fp, excludes):
                continue
            if fp.suffix in PY_EXTS:
                py_files.append(fp)
            else:
                other_files.append(fp)
        if py_files:
            outline.append("**Python modules**")
            for pf in py_files:
                r = pf.relative_to(root).as_posix()
                classes, funcs = scan_python_symbols(pf)
                meta = []
                if classes: meta.append("classes: " + ", ".join(classes[:6]) + (" ..." if len(classes)>6 else ""))
                if funcs: meta.append("funcs: " + ", ".join(funcs[:6]) + (" ..." if len(funcs)>6 else ""))
                info = f" — {', '.join(meta)}" if meta else ""
                outline.append(f"- `{r}`{info}")
        if other_files:
            outline.append("**Other files**")
            for of in other_files:
                r = of.relative_to(root).as_posix()
                outline.append(f"- `{r}`")
        if py_files or other_files:
            outline.append("")
    return "\n".join(outline).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--out", default="runtime/repo_map.md")
    ap.add_argument("--exclude", default=",".join(sorted(DEFAULT_EXCLUDES)))
    args = ap.parse_args()

    root = Path(args.root).resolve()
    excludes = set([x.strip() for x in args.exclude.split(",") if x.strip()])

    content = [
        "# Repository Map",
        "",
        f"_Generated from: {root}_",
        "",
        build_map(root, excludes) or "_No files found (check filters)._" 
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(content), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
