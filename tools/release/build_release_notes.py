#!/usr/bin/env python
from __future__ import annotations

import argparse
import pathlib
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--since-tag")
    args = parser.parse_args()

    template_path = pathlib.Path(args.template)
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    text = template_path.read_text(encoding="utf-8")

    bullets = ""
    if args.since_tag:
        try:
            log = subprocess.check_output(
                ["git", "log", f"{args.since_tag}..HEAD", "--oneline"],
                text=True,
            )
            bullets = "\n".join(
                f"- {line.strip()}" for line in log.strip().splitlines()
            )
        except subprocess.CalledProcessError:
            bullets = ""

    content = text.replace("{{CHANGELOG}}", bullets)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote release notes to {out_path}")


if __name__ == "__main__":
    main()
