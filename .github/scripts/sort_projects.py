#!/usr/bin/env python3
"""Sort the README "Selected projects" table by GitHub stars, then forks."""

import json
import os
import re
import urllib.request

README = "README.md"
ROW = re.compile(r"^\|\s+\[\*\*.+?\*\*\]\(https://github\.com/([^/)]+/[^/)]+)\)")


def counts(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}")
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    return data["stargazers_count"], data["forks_count"]


lines = open(README).read().split("\n")
idx = [i for i, l in enumerate(lines) if ROW.match(l)]
assert idx and idx == list(range(idx[0], idx[-1] + 1)), "table rows not contiguous"

rows = [lines[i] for i in idx]
rows.sort(key=lambda l: counts(ROW.match(l).group(1)), reverse=True)
lines[idx[0] : idx[-1] + 1] = rows
open(README, "w").write("\n".join(lines))
