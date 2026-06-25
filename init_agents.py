#!/usr/bin/env python3
"""Install the bundled `.agents/` project brain into a target repository.

The template lives next to this script (./.agents/). This installer copies it into
a target repo's root, idempotently and safely:

  * By default it NEVER overwrites files that already exist in the target — it only
    adds missing ones. So re-running is a safe no-op once installed.
  * --force overwrites existing files, but first backs up the target's current
    .agents/ to a timestamped .zip beside it.
  * --dry-run prints the plan and writes nothing.
  * --check verifies the target has every expected file (exit 0 = complete).

Usage:
    python init_agents.py [--target DIR] [--dry-run] [--force] [--check]

No third-party dependencies. Python 3.8+.
"""
import argparse
import datetime as _dt
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _template_items():
    """Yield tuples of (source_absolute_path, target_relative_path)."""
    # 1. `.agents/` directory
    agents_dir = os.path.join(HERE, ".agents")
    if os.path.isdir(agents_dir):
        for root, _, files in os.walk(agents_dir):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, agents_dir)
                yield full, os.path.join(".agents", rel)

    # 2. `launcher/` directory
    launcher_dir = os.path.join(HERE, "launcher")
    if os.path.isdir(launcher_dir):
        for root, _, files in os.walk(launcher_dir):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, launcher_dir)
                yield full, os.path.join("launcher", rel)

    # 3. Individual files in the root
    for item in ["run.bat", "run.sh"]:
        full = os.path.join(HERE, item)
        if os.path.isfile(full):
            yield full, item


def _backup(dest_agents):
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = os.path.join(os.path.dirname(dest_agents),
                          ".agents-backup-%s.zip" % stamp)
    with zipfile.ZipFile(backup, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(dest_agents):
            for name in files:
                full = os.path.join(root, name)
                arc = os.path.relpath(full, os.path.dirname(dest_agents))
                zf.write(full, arc)
    return backup


def cmd_check(target):
    missing = []
    for src, rel in _template_items():
        if not os.path.isfile(os.path.join(target, rel)):
            missing.append(rel)
    if missing:
        print("INCOMPLETE — %d file(s) missing under %s:" % (len(missing), target))
        for m in sorted(missing):
            print("  - %s" % m.replace(os.sep, "/"))
        return 1
    total = sum(1 for _ in _template_items())
    print("OK — all %d starter pack files present under %s" % (total, target))
    return 0


def cmd_install(target, dry_run, force):
    agents_dir = os.path.join(HERE, ".agents")
    if not os.path.isdir(agents_dir):
        print("error: template brain not found at %s" % agents_dir, file=sys.stderr)
        return 1
    dest_agents = os.path.join(target, ".agents")

    if force and os.path.isdir(dest_agents) and not dry_run:
        b = _backup(dest_agents)
        print("backed up existing .agents/ -> %s" % b)

    created, skipped, overwritten = [], [], []
    for src, rel in sorted(_template_items(), key=lambda x: x[1]):
        dst = os.path.join(target, rel)
        exists = os.path.isfile(dst)
        if exists and not force:
            skipped.append(rel)
            continue
        (overwritten if exists else created).append(rel)
        if not dry_run:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    prefix = "[dry-run] would " if dry_run else ""
    for rel in created:
        print("%screate   %s" % (prefix, rel.replace(os.sep, "/")))
    for rel in overwritten:
        print("%soverwrite %s" % (prefix, rel.replace(os.sep, "/")))
    for rel in skipped:
        print("skip     %s (exists — use --force to overwrite)" % rel.replace(os.sep, "/"))

    print("\nsummary: %d created, %d overwritten, %d skipped%s"
          % (len(created), len(overwritten), len(skipped),
             " (dry-run, nothing written)" if dry_run else ""))
    if not dry_run and (created or overwritten):
        print("next: fill in <PLACEHOLDER> tokens in .agents/ and configure run.bat.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Install the .agents/ project brain.")
    ap.add_argument("--target", default=".", help="target repo root (default: current dir)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; write nothing")
    ap.add_argument("--force", action="store_true", help="overwrite existing files (backs up first)")
    ap.add_argument("--check", action="store_true", help="verify install is complete; exit 0/1")
    args = ap.parse_args(argv)

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        print("error: target dir does not exist: %s" % target, file=sys.stderr)
        return 2

    if args.check:
        return cmd_check(target)
    return cmd_install(target, args.dry_run, args.force)


if __name__ == "__main__":
    raise SystemExit(main())
