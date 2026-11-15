#!/usr/bin/env python3
import json, os, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
MANIFEST = REPO / "finalpool_manifest.json"
DEST = REPO / "tasks" / "finalpool"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True)

def dev_dir(branch):
    return branch.replace("-dev", "").replace("_dev", "")

def main():
    entries = json.loads(MANIFEST.read_text())
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True, exist_ok=True)
    seen = set()
    copied_files = 0
    for e in entries:
        branch, task = e["branch"], e["task"]
        if task in seen:
            raise SystemExit(f"Duplicate task name in manifest: {task}")
        seen.add(task)
        src = f"tasks/{dev_dir(branch)}/{task}"
        ref = f"origin/{branch}"
        paths = git("ls-tree", "-r", "--name-only", ref, "--", src).splitlines()
        if not paths:
            raise SystemExit(f"No files found for {ref}:{src}")
        for p in paths:
            rel = p[len(src)+1:]
            if not rel:
                continue
            out = DEST / task / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            data = subprocess.check_output(["git", "show", f"{ref}:{p}"], cwd=REPO)
            out.write_bytes(data)
            copied_files += 1
    print(f"Copied {len(seen)} tasks and {copied_files} files into tasks/finalpool")

if __name__ == "__main__":
    main()
