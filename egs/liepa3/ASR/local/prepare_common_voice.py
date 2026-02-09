#!/usr/bin/env python3
import argparse
import logging
import os
from dataclasses import replace

from lhotse import CutSet

from prepare_corpus import clean_text


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="""Input cut from lhotse.
        """,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="""Output file.
            """,
    )

    return parser.parse_args()


def main():
    args = get_args()

    logging.info(f"preparing common voice text from {args.input}")

    cuts = CutSet.from_file(args.input)

    def normalize(s):
        s.text = clean_text(s.text)
        return s

    logging.info(f"normalize texts")
    cuts = cuts.map(normalize)

    logging.info(f"writing cuts to {args.output}")
    cuts.to_file(args.output)
    logging.info("done")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
