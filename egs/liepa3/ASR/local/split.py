import argparse
import logging
import os
import random
from pathlib import Path

from lhotse import CutSet

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-dir",
        type=str,
        help="""Manifest dir.
        """,
    )
    args = parser.parse_args()

    random.seed(42)

    manifest_path = Path(args.manifest_dir)

    cuts = CutSet.from_file(manifest_path / "cuts_all.jsonl.gz")
    cuts = cuts.shuffle()

    n = len(cuts)
    logging.info(f"All {n}")
    n_train = int(0.9 * n)
    n_dev = int(0.05 * n)

    cuts_train = cuts.subset(first=n_train)
    cuts_dev = cuts.subset(first=n_train + n_dev).subset(last=n_dev)
    cuts_test = cuts.subset(last=n - n_train - n_dev)

    logging.info(f"Train cuts: {len(cuts_train)}")
    logging.info(f"Dev   cuts: {len(cuts_dev)}")
    logging.info(f"Test  cuts: {len(cuts_test)}")

    cuts_train.to_file(manifest_path / "cuts_train.jsonl.gz")
    cuts_dev.to_file(manifest_path / "cuts_dev.jsonl.gz")
    cuts_test.to_file(manifest_path / "cuts_test.jsonl.gz")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
