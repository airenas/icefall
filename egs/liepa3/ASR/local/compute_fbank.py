#!/usr/bin/env python3


"""
This file computes fbank features for cuts file.
It looks for manifests in the directory data/manifests.

The generated fbank features are saved in data/fbank.
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

import sentencepiece as spm
import torch
from lhotse import CutSet, Fbank, FbankConfig, LilcomChunkyWriter

from egs.liepa3.ASR.local.filter_cuts import filter_cuts
from icefall.utils import get_executor, str2bool

# Torch's multithreaded behavior needs to be disabled or
# it wastes a lot of CPU and slow things down.
# Do this outside of main() in case it needs to take effect
# even when we are not invoking the main (e.g. when spawning subprocesses).
torch.set_num_threads(1)
torch.set_num_interop_threads(1)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bpe-model",
        type=str,
        help="""Path to the bpe.model. If not None, we will remove short and
        long utterances before extracting features""",
    )

    parser.add_argument(
        "--cuts",
        type=str,
        required=True,
        help="""Cuts file to compute fbank""",
    )

    parser.add_argument(
        "--partition",
        type=str,
        required=True,
        help="""Name of the partition to save fbank, e.g. train, test, dev""",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="""Output dir to compute fbank""",
    )

    parser.add_argument(
        "--perturb-speed",
        type=str2bool,
        default=True,
        help="""Perturb speed with factor 0.9 and 1.1 on train subset.""",
    )

    return parser.parse_args()


def compute_fbank(
        bpe_model: Optional[str] = None,
        cuts: str = None,
        output_dir: str = None,
        perturb_speed: Optional[bool] = True,
        partition: Optional[str] = None,
):
    logging.info(f"files to process: {cuts}")
    logging.info(f"partition: {partition}")
    logging.info(f"perturb_speed: {perturb_speed}")
    logging.info(f"bpe_model: {bpe_model}")
    logging.info(f"output_dir: {output_dir}")

    output_dir = Path(output_dir)
    num_jobs = min(30, os.cpu_count())
    num_mel_bins = 80

    if bpe_model:
        logging.info(f"Loading {bpe_model}")
        sp = spm.SentencePieceProcessor()
        sp.load(bpe_model)

    extractor = Fbank(FbankConfig(num_mel_bins=num_mel_bins))
    cuts_file = Path(cuts)
    with get_executor() as ex:  # Initialize the executor only once.
        if not cuts_file.is_file():
            raise RuntimeError(f"{cuts_file} not found - skipping")

        cuts_filename = cuts_file.name
        logging.info(f"Processing {cuts_filename}")
        cut_set = CutSet.from_file(cuts_file)

        if bpe_model:
            cut_set = filter_cuts(cut_set, sp)
        if perturb_speed:
            logging.info(f"Doing speed perturb")
            cut_set = (
                    cut_set
                    + cut_set.perturb_speed(0.9)
                    + cut_set.perturb_speed(1.1)
            )

        logging.info("resampling to 16kHz and extracting features")
        cut_set = cut_set.resample(16000)
        cut_set = cut_set.compute_and_store_features(
            extractor=extractor,
            storage_path=f"{output_dir}/feats_{partition}",
            # when an executor is specified, make more partitions
            num_jobs=num_jobs if ex is None else 80,
            executor=ex,
            storage_type=LilcomChunkyWriter,
        )
        cut_set.to_file(output_dir / cuts_filename)


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    args = get_args()
    logging.info(vars(args))
    compute_fbank(
        bpe_model=args.bpe_model,
        cuts=args.cuts,
        output_dir=args.output_dir,
        perturb_speed=args.perturb_speed,
        partition=args.partition,
    )

    logging.info("Done")
