import argparse
import logging
import os
import random
from pathlib import Path

from lhotse import CutSet


def take(cuts, n, max_duration: int):
    res = []
    total_duration = 0
    for cut in cuts:
        res.append(cut) # make sure we add otherwise could be lost in the next iteration
        total_duration += cut.duration
        if 0 < max_duration <= total_duration:
            break
        if len(res) >= n:
            break
    return CutSet.from_cuts(res), total_duration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-dir",
        type=str,
        help="""Manifest dir.
        """,
    )
    parser.add_argument(
        "--max-duration",
        type=int,
        default=36000,
        help="Limit test/dev dataset to this many secs (0 = no limit)",
    )
    args = parser.parse_args()
    logging.info(f"Splitting data in {args.manifest_dir} with max_duration={args.max_duration}s")

    random.seed(42)

    manifest_path = Path(args.manifest_dir)

    cuts = CutSet.from_file(manifest_path / "cuts_all.jsonl.gz")
    cuts = cuts.shuffle()

    n = len(cuts)
    logging.info(f"All {n}")
    n_dev = int(0.05 * n)

    ci = iter(cuts)

    cuts_dev, duration = take(ci, n_dev, args.max_duration)
    logging.info(f"Dev   cuts: {len(cuts_dev)}. Duration: {duration/3600:.2f} hours")
    cuts_test, duration = take(ci, n_dev, args.max_duration)
    logging.info(f"Train  cuts: {len(cuts_test)}. Duration: {duration / 3600:.2f} hours")
    cuts_train, duration = take(ci, n, 0)
    logging.info(f"Train  cuts: {len(cuts_train)}. Duration: {duration / 3600:.2f} hours")

    cuts_train.to_file(manifest_path / "cuts_train.jsonl.gz")
    cuts_dev.to_file(manifest_path / "cuts_dev.jsonl.gz")
    cuts_test.to_file(manifest_path / "cuts_test.jsonl.gz")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
