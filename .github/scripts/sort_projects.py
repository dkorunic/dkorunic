#!/usr/bin/env python3
"""Sync the README "Selected projects" table descriptions with GitHub, then
sort it by stars and forks."""

import json
import os
import re
import urllib.request

README = "README.md"
ROW = re.compile(r"^\|\s+\[\*\*.+?\*\*\]\(https://github\.com/([^/)]+/[^/)]+)\)")
DESC = 2  # description column index in a "|"-split row


def fetch(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def plain(s):
    # README may add markdown and a trailing period; ignore them when comparing
    return re.sub(r"[_`]", "", s.strip()).rstrip(".")


lines = open(README).read().split("\n")
idx = [i for i, l in enumerate(lines) if ROW.match(l)]
assert idx and idx == list(range(idx[0], idx[-1] + 1)), "table rows not contiguous"

rows = []
for i in idx:
    data = fetch(ROW.match(lines[i]).group(1))
    cells = lines[i].split("|")
    assert len(cells) == 7, f"unexpected row: {lines[i]}"
    desc = (data["description"] or "").strip()
    if desc and plain(cells[DESC]) != plain(desc):
        cells[DESC] = desc if desc.endswith(".") else desc + "."
    rows.append(((data["stargazers_count"], data["forks_count"]), cells))
rows.sort(key=lambda r: r[0], reverse=True)

# re-pad the description column so the table stays aligned
head, sep = (lines[idx[0] - 2].split("|"), lines[idx[0] - 1].split("|"))
table = [head] + [c for _, c in rows]
width = max(len(c[DESC].strip()) for c in table)
for c in table:
    c[DESC] = f" {c[DESC].strip().ljust(width)} "
sep[DESC] = f" {'-' * width} "

lines[idx[0] - 2] = "|".join(head)
lines[idx[0] - 1] = "|".join(sep)
lines[idx[0] : idx[-1] + 1] = ["|".join(c) for _, c in rows]
open(README, "w").write("\n".join(lines))
