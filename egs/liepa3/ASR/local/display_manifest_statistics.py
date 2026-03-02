"""
This file displays duration statistics of utterances in a manifest.
You can use the displayed value to choose minimum/maximum duration
to remove short and long utterances during the training.

See the function `remove_short_and_long_utt()` in transducer/train.py
for usage.
"""
import argparse
import logging
import os
from pathlib import Path

import torch
from lhotse import load_manifest_lazy
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cuts-file",
        type=Path,
        help="""Transcript file.
        """,
    )
    return parser.parse_args()


def test_for_bad_cuts(cuts):
    bad = []
    pbar = tqdm(cuts, desc="Checking cuts for bad features")
    for c in pbar:
        feats = c.load_features()
        feats_tensor = torch.tensor(feats)
        if torch.isnan(feats_tensor).any() or torch.isinf(feats_tensor).any():
            bad.append(c.id)
        pbar.set_postfix({"bad cuts": len(bad)})
           

    logging.info(f"Number of bad cuts: {len(bad)}")
    logging.info(f"Example bad cut IDs: {bad[:10]}")
    return len(bad) == 0


def main():
    args = get_args()

    path = args.cuts_file

    cuts = load_manifest_lazy(path)
    cuts.describe()
    if test_for_bad_cuts(cuts):
        logging.info("Cuts OK")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
