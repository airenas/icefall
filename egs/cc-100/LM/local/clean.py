#!/usr/bin/env python3
import argparse
import logging
import os

from tqdm import tqdm

from egs.liepa3.ASR.local.text_utils import clean_text


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="""Input text file.
        """,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="""Output file
            """,
    )

    return parser.parse_args()


def skip(line):
    """Decide whether to skip the line.
    If line contains  numeric characters
    If line contains email, url
    """
    if any(c.isdigit() for c in line):
        return True
    if "@" in line:
        return True
    if "/" in line:  # make sure no urls
        return True
    return False


def main():
    args = get_args()

    logging.info(f"skipping and normalizing {args.input}")

    read, wrote, skipped = 0, 0, 0

    with open(args.output, "w", encoding="utf-8") as f_out:
        with open(args.input, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc="Reading file"):
                line = line.rstrip("\n")
                read += 1
                if skip(line):
                    skipped += 1
                    continue
                cleaned, ok = clean_text(line)
                if not ok or len(cleaned) < 10: # skip too short sentences, perhaps bad splitting into sentences
                    skipped += 1
                    continue
                wrote += 1
                f_out.write(cleaned + "\n")
    logging.info(f"read {read}, wrote {wrote}, skipped {skipped} sentences")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
