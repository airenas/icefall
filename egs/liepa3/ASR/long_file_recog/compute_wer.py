#!/usr/bin/env python3

"""
This file calculates wer
"""

import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import sentencepiece as spm
from lhotse import (
    CutSet,
    MonoCut,
    SupervisionSegment,
    SupervisionSet,
    load_manifest,
)
from lhotse.cut import Cut
from lhotse.serialization import SequentialJsonlWriter

from egs.liepa3.ASR.zipformer.decode import save_wer_results
from egs.liepa3.ASR.zipformer.decode import save_asr_output
from icefall import AttributeDict


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--manifest-in",
        type=Path,
        default=Path("data/librilight/manifests_chunk_recog"),
        help="Path to file of cuts with text (wanted)) and hypothesis recorded in the custom attribute.",
    )

    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/results"),
        help="Path to dir to save WER results.",
    )

    parser.add_argument(
        "--name",
        type=str,
        help="Cuts name, used as a part of result file names",
    )
    return parser.parse_args()


def merge_chunks(
        cuts_chunk: CutSet,
        supervisions: SupervisionSet,
        cuts_writer: SequentialJsonlWriter,
        sp: spm.SentencePieceProcessor,
        extra: float,
) -> int:
    """Merge chunk-wise cuts accroding to recording ids.

    Args:
      cuts_chunk:
        The chunk-wise cuts opened in a lazy mode.
      supervisions:
        The supervision manifest containing text file path, opened in a lazy mode.
      cuts_writer:
        Writer to save the cuts with recognition results.
      sp:
        The BPE model.
      extra:
        Extra duration (in seconds) to drop at both sides of each chunk.
    """

    #  Background worker to add alignemnt and save cuts to disk.
    def _save_worker(utt_cut: Cut, flush=False):
        cuts_writer.write(utt_cut, flush=flush)

    def _merge(cut_list: List[Cut], rec_id: str, utt_idx: int):
        """Merge chunks with same recording_id."""
        for cut in cut_list:
            assert cut.recording.id == rec_id, (cut.recording.id, rec_id)

        # For each group with a same recording, sort it accroding to the start time
        # In fact, we don't need to do this since the cuts have been sorted
        # according to the start time
        cut_list = sorted(cut_list, key=(lambda cut: cut.start))

        rec = cut_list[0].recording
        alignments = []
        cur_end = 0
        for cut in cut_list:
            # Get left and right borders
            left = cut.start + extra if cut.start > 0 else 0
            chunk_end = cut.start + cut.duration
            right = chunk_end - extra if chunk_end < rec.duration else rec.duration

            # Assert the chunks are continuous
            assert left == cur_end, (left, cur_end)
            cur_end = right

            assert len(cut.supervisions) == 1, len(cut.supervisions)
            for ali in cut.supervisions[0].alignment["symbol"]:
                t = ali.start + cut.start
                if left <= t < right:
                    alignments.append(ali.with_offset(cut.start))

        tokens = [ali.symbol for ali in alignments]
        hyp = sp.decode(tokens)

        # old_sup = supervisions[rec_id]
        # all cuts have the same supervision, and the supervision id is the same as recording id
        old_sup = cut_list[0].supervisions[0]
        # Assuming the supervisions are sorted with the same recoding order as in cuts_chunk
        # old_sup = supervisions[utt_idx]
        assert old_sup.recording_id == rec_id, (old_sup.recording_id, rec_id)

        new_sup = SupervisionSegment(
            id=rec_id,
            recording_id=rec_id,
            start=0,
            duration=rec.duration,
            alignment={"symbol": alignments},
            language=old_sup.language,
            speaker=old_sup.speaker,
            text=old_sup.text,
            custom={"hypothesis": hyp},
        )

        utt_cut = MonoCut(
            id=rec_id,
            start=0,
            duration=rec.duration,
            channel=0,
            recording=rec,
            supervisions=[new_sup],
        )
        # Set a custom attribute to the cut
        # utt_cut.text_path = old_sup.book

        return utt_cut

    last_rec_id = None
    cut_list = []
    utt_idx = 0

    futures = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for cut in cuts_chunk:
            cur_rec_id = cut.recording.id
            if len(cut_list) == 0:
                # Case of the first cut
                last_rec_id = cur_rec_id
                cut_list.append(cut)
            elif cur_rec_id == last_rec_id:
                cut_list.append(cut)
            else:
                # Case of a cut belonging to a new recording
                utt_cut = _merge(cut_list, last_rec_id, utt_idx)
                utt_idx += 1

                futures.append(executor.submit(_save_worker, utt_cut))

                last_rec_id = cur_rec_id
                cut_list = [cut]

                if utt_idx % 5000 == 0:
                    logging.info(f"Procesed {utt_idx} utterances.")

        # For the cuts belonging to the last recording
        if len(cut_list) != 0:
            utt_cut = _merge(cut_list, last_rec_id, utt_idx)
            utt_idx += 1

            futures.append(executor.submit(_save_worker, utt_cut))
            logging.info("Finished")

        for f in futures:
            f.result()

    return utt_idx


def main():
    args = get_parser()

    logging.info(f"Processing {args.manifest_in} cut")

    cuts = load_manifest(args.manifest_in)  # We will use the text path from supervisions
    logging.info(f"Loaded {len(cuts)} cuts")
    results = []
    for cut in cuts:
        utt_id = cut.id
        sup = cut.supervisions[0]
        ref_words = sup.text.split()
        hyp_words = sup.custom["hypothesis"].split()
        results.append((utt_id, ref_words, hyp_words))

    results_dict = {"greedy_search": results}
    params = AttributeDict(
        {
            "res_dir": args.out_dir,
            "suffix": "",
        }
    )
    save_asr_output(params, args.name, results_dict)
    save_wer_results(params, args.name, results_dict)




if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter, level=logging.INFO)
    logging.info("Started")
    main()
    logging.info("Done")
