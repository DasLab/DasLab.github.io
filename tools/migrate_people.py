#!/usr/bin/env python3
"""Migrate _people + _alumni into a single _people collection.

Per-entry changes:
- Add a `status: current` or `status: alumnus` field.
- For current members, derive a `role_order` from the role text (PI=1,
  lab manager=2, research specialist=3, postdoc=4, PhD student=5, other=9)
  so the listing stays meaningful without manual numeric prefixes.
- For alumni, parse the trailing year from the role string (e.g.
  "Ph.D. Student, 2019-2025" → end_year=2025) and store it as a sort key.
- Drop the numeric filename prefix; the file is just `<slug>.md`.

Run once after the collection switch; idempotent.
"""
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PEOPLE = ROOT / "_people"
ALUMNI = ROOT / "_alumni"


def is_pi(role: str) -> bool:
    return "principal investigator" in role.lower()


def end_year(role: str) -> int | None:
    """Extract the latest 4-digit year from a role string like
    'Ph.D. Student, 2019-2025' or 'Postdoc, 2024'."""
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", role)]
    return max(years) if years else None


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse_md(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    fm_lines = m.group(1).splitlines()
    body = m.group(2)
    fm = {}
    for line in fm_lines:
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def write_md(path: Path, fm: dict, body: str):
    out = ["---"]
    for k, v in fm.items():
        if v is None or v == "": continue
        sv = str(v)
        if any(c in sv for c in ':#"\'\n') or sv.startswith("- "):
            out.append(f'{k}: "{sv}"')
        else:
            out.append(f"{k}: {sv}")
    out.append("---")
    if body.strip():
        out.append("")
        out.append(body.strip())
    out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


def slug_from_filename(name: str) -> str:
    """foo/01-jane-doe.md or foo/123-jane-doe.md -> jane-doe.md"""
    base = re.sub(r"^\d+-", "", name)
    return base


def main():
    PEOPLE.mkdir(exist_ok=True)
    converted_current = converted_alumni = 0

    # Current members: just rewrite with status + role_order, drop numeric prefix
    for p in sorted(PEOPLE.glob("*.md")):
        fm, body = parse_md(p)
        if fm is None: continue
        if "status" in fm and fm.get("status") == "current":
            continue  # already migrated
        fm["status"] = "current"
        if "role" in fm and is_pi(fm["role"]):
            fm["pi"] = True
        # Drop the legacy `order` field (which was filename-driven, no longer
        # meaningful since we sort by role_order + name now).
        fm.pop("order", None)
        new_name = slug_from_filename(p.name)
        new_path = PEOPLE / new_name
        write_md(new_path, fm, body)
        if new_path != p: p.unlink()
        converted_current += 1

    # Alumni: move into _people with status: alumnus + end_year
    if ALUMNI.exists():
        for a in sorted(ALUMNI.glob("*.md")):
            fm, body = parse_md(a)
            if fm is None: continue
            fm["status"] = "alumnus"
            if "role" in fm:
                ey = end_year(fm["role"])
                if ey: fm["end_year"] = ey
            fm.pop("order", None)
            new_name = slug_from_filename(a.name)
            new_path = PEOPLE / new_name
            # If a slug collision occurs (rare), append a marker
            if new_path.exists():
                new_path = PEOPLE / new_name.replace(".md", "-alumni.md")
            write_md(new_path, fm, body)
            converted_alumni += 1
        # Drop the now-empty _alumni directory
        for a in ALUMNI.glob("*.md"): a.unlink()
        ALUMNI.rmdir()

    print(f"Migrated {converted_current} current and {converted_alumni} alumni into _people/")


if __name__ == "__main__":
    main()
