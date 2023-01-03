#!/usr/bin/python

import os
import sys
import re

argc = len(sys.argv)

link_pattern = sys.argv[1]
files = sys.argv[2:]

# match any a even if the text part in on different line
link = re.compile(r'<a href="({l})">'.format(l=link_pattern))
comment_start = re.compile(r"^\s*<!--")
comment_end = re.compile(r"-->\s*$")

entries = []

for name in files:
    with open(name, "r") as f:
        in_comment = False
        for line in f:
            if comment_start.search(line):
                in_comment = True
            if not in_comment:
                match = link.search(line)
                if match:
                    entries.append((match.group(1), name))
            if comment_end.search(line):
                in_comment = False

# remove anchor part
entries = [(entry.split("#")[0], origin) for entry, origin in entries]

# only unique entries, preserved only the first one
unique_entries = []
for entry, origin in entries:
    if entry not in unique_entries:
        if not os.path.exists(entry) and not entry.startswith("http"):
            print(
                "WARNING: {link} extracted from {file} does not exist as local file"
                " and it does not look like an URL".format(link=entry, file=origin),
                file=sys.stderr,
            )
        unique_entries.append(entry)

# print in one line
sys.stdout.write(" ".join(unique_entries))
