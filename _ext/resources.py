"""The `resource-list` directive: renders data/resources.yaml as a wiki list.

Records live in data/resources.yaml (the schema is documented at the top of
that file). A topic is valid iff docs/topics/<topic>.md exists. Any bad data
raises ExtensionError, which aborts the build instead of rendering nothing.
"""

from pathlib import Path

import yaml
from sphinx.errors import ExtensionError

# kind -> group heading, in display order. This is also the list of allowed kinds.
KINDS = {
    "paper": "Papers",
    "lecture": "Lectures",
    "video": "Videos",
    "course": "Courses",
    "book": "Books",
    "blog": "Blog posts",
    "code": "Code",
    "notebook": "Notebooks",
}
LEVELS = ("foundational", "intermediate", "advanced")
OURS = "Our material"  # heading for `doc:` records, always shown first

FIELDS = {  # field -> type
    "id": str,
    "url": str,
    "doc": str,
    "title": str,
    "kind": str,
    "topics": list,
    "level": str,
    "year": int,
    "note": str,
}
REQUIRED = {"id", "kind", "topics", "level"}


def load(path, valid_topics):
    """Read and validate the YAML at `path`; return the list of records."""
    records = yaml.safe_load(Path(path).read_text()) or []
    if not isinstance(records, list):
        raise ExtensionError(f"{path}: expected a list of records")
    seen = set()
    for i, r in enumerate(records):
        name = r.get("id", f"#{i}") if isinstance(r, dict) else f"#{i}"

        def check(ok, problem):
            if not ok:
                raise ExtensionError(f"{path}: record {name}: {problem}")

        check(isinstance(r, dict), "not a mapping")
        check(not (unknown := r.keys() - FIELDS), f"unknown field(s) {sorted(unknown)}")
        check(not (missing := REQUIRED - r.keys()), f"missing field(s) {sorted(missing)}")
        for key, value in r.items():
            check(isinstance(value, FIELDS[key]), f"{key} must be {FIELDS[key].__name__}")
        check(("url" in r) != ("doc" in r), "needs exactly one of url/doc")
        check("doc" in r or "title" in r, "url records need a title")
        check(r["kind"] in KINDS, f"unknown kind {r['kind']!r}, expected one of {list(KINDS)}")
        check(r["level"] in LEVELS, f"unknown level {r['level']!r}, expected one of {LEVELS}")
        check(r["topics"], "topics is empty")
        bad = set(r["topics"]) - valid_topics
        check(not bad, f"unknown topic(s) {sorted(bad)}; add docs/topics/<topic>.md first")
        check(name not in seen, "duplicate id")
        seen.add(name)
    return records


def group(records, topics=None):
    """Filter by `topics` (None = all) and return [(heading, records)], empty groups dropped."""
    picked = [r for r in records if topics is None or set(r["topics"]) & set(topics)]
    groups = [(OURS, [r for r in picked if "doc" in r])]
    groups += [(h, [r for r in picked if "url" in r and r["kind"] == k]) for k, h in KINDS.items()]
    return [(heading, rs) for heading, rs in groups if rs]
