#!/usr/bin/env python3
"""
Select the most relevant files in the repo for a given task string.
Heuristic, stdlib-only scoring (name hits > content hits).

Usage:
  python tools/context_budgeter.py --root . --task "implement schedule engine" --limit 25 --out runtime/context_files.md \
    --include_ext .py,.md,.yaml,.yml,.json --exclude venv,node_modules,.git,__pycache__

Outputs rationale and matched lines.
"""
import os, argparse, re
from pathlib import Path
from collections import Counter, defaultdict

DEFAULT_EXCLUDES = {"venv","node_modules",".git","__pycache__",".mypy_cache",".pytest_cache",".ruff_cache","dist","build"}
DEFAULT_EXTS = {".py",".md",".yaml",".yml",".json",".toml",".ini"}

def tokenize(s: str):
    return [t.lower() for t in re.findall(r"[A-Za-z0-9_]{2,}", s)]

def score_file(path: Path, task_tokens, max_bytes=150_000):
    name = path.name.lower()
    with path.open("rb") as f:
        blob = f.read(max_bytes)
    text = blob.decode("utf-8", errors="ignore")
    # weights
    name_score = sum(name.count(tok) for tok in task_tokens) * 3
    # simple occurrence in content
    content_score = 0
    matches_by_line = defaultdict(int)
    for tok in task_tokens:
        for m in re.finditer(re.escape(tok), text.lower()):
            content_score += 1
            # track line number
            line_no = text.count("\n", 0, m.start()) + 1
            matches_by_line[line_no] += 1
    # path depth preference (shallower is slightly preferred)
    depth_bonus = max(0, 5 - len(path.parts)) * 0.2
    score = name_score + content_score + depth_bonus
    return score, matches_by_line, text

def should_skip(p: Path, excludes):
    return any(part in excludes for part in p.parts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--task", required=True)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--out", default="runtime/context_files.md")
    ap.add_argument("--include_ext", default=",".join(sorted(DEFAULT_EXTS)))
    ap.add_argument("--exclude", default=",".join(sorted(DEFAULT_EXCLUDES)))
    args = ap.parse_args()

    root = Path(args.root).resolve()
    excludes = set([x.strip() for x in args.exclude.split(",") if x.strip()])
    include_exts = set([x.strip() for x in args.include_ext.split(",") if x.strip()])

    task_tokens = tokenize(args.task)
    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        p = Path(dirpath)
        if should_skip(p, excludes):
            dirnames[:] = [d for d in dirnames if d not in excludes]
            continue
        for fn in filenames:
            fp = p / fn
            if fp.suffix.lower() not in include_exts: 
                continue
            if should_skip(fp, excludes): 
                continue
            try:
                s, lines, text = score_file(fp, task_tokens)
                candidates.append((s, fp, lines, text))
            except Exception:
                pass

    candidates.sort(key=lambda x: x[0], reverse=True)
    top = candidates[: max(1, args.limit)]

    out_lines = ["# Context File Picks",
                 "",
                 f"_Task: {args.task} • Repo: {root}_",
                 ""]
    for rank, (s, fp, lines, text) in enumerate(top, 1):
        rel = fp.relative_to(root).as_posix()
        out_lines.append(f"## {rank}. `{rel}` — score {s:.2f}")
        if lines:
            show = sorted(lines.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
            out_lines.append("Matched lines: " + ", ".join([f"{ln}:{cnt}" for ln, cnt in show]))
            # include small snippet for the most matched line
            best_ln = show[0][0] if show else 1
            snippet = "\n".join(text.splitlines()[max(0,best_ln-3):best_ln+2])
            out_lines.append("\n```text\n" + snippet + "\n```\n")
        else:
            out_lines.append("_No specific line matches (likely name/path relevance)._")
        out_lines.append("")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Wrote {out} with {len(top)} files")

if __name__ == "__main__":
    main()
