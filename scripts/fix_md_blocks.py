#!/usr/bin/env python3
import sys


def fix_markdown(file_path):
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    in_block = False
    for line in lines:
        if line.strip() == "```text":
            if in_block:
                new_lines.append("```\n")
                in_block = False
            else:
                new_lines.append("```text\n")
                in_block = True
        else:
            new_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        fix_markdown(arg)
