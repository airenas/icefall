#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path

from lhotse import RecordingSet, SupervisionSet, CutSet, Recording, SupervisionSegment
from tqdm import tqdm

from egs.liepa3.ASR.local.text_utils import clean_text, clean_tags, drop_sil


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus-dir",
        type=str,
        help="""Corpus dir.
        """,
    )
    parser.add_argument(
        "--transcript-file",
        type=str,
        help="""Transcript file.
        """,
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="""Output file.
            """,
    )

    parser.add_argument(
        "--audio-pattern",
        type=str,
        default="{0}_{1}.waw",
        help="""Audio file pattern.
            """,
    )

    return parser.parse_args()


def main():
    args = get_args()

    logging.info(f"collecting files from {args.corpus_dir} and transcripts from {args.transcript_file}")

    recordings = []
    supervisions = []

    corpus_dir = Path(args.corpus_dir)
    transcript_file = Path(args.transcript_file)

    count = 0

    files = []
    previous_f = None
    previous_t = ""

    with open(transcript_file, newline="", encoding="utf-8-sig") as file:
        for line_id, line in enumerate(tqdm(file, desc="Processing cv file")):
            line = line.strip()
            if not line:
                continue
            row = line.split(" ", maxsplit=1)
            f, utt_text = row[0], row[1]
            logging.info(f"file: {f}")
            fs = f.split("_")
            fn = args.audio_pattern
            for i, s in enumerate(fs):
                fn = fn.replace("{" + str(i) + "}", s)
            if previous_f == fn:
                previous_t += " " + utt_text
                continue
            if previous_f:
                files.append((previous_f, previous_t))
            previous_f = fn
            previous_t = utt_text
            logging.info(f"audio: {str(fn)}")
    if previous_f:
        files.append((previous_f, previous_t))

    logging.info(f"Found {len(files)} files")

    for line_id, (fn, utt_text) in enumerate(tqdm(files, desc="Processing files")):
        audio_path = corpus_dir / fn
        # logging.info(f"audio: {str(audio_path)}")

        # Recording object (per utterance or per file, here per utterance)
        if not audio_path.is_file():
            logging.warning(
                "Audio file '%s' not found, skipping",
                audio_path,
            )
            continue
        recording = Recording.from_file(audio_path, recording_id=str(line_id))
        duration = recording.duration

        text = clean_tags(utt_text)
        text, ok = clean_text(text)
        if not ok:
            logging.warning(
                "Text contains invalid characters '%s'",
                utt_text,
            )
            continue
        text = drop_sil(text, "sil")
        text = drop_sil(text, "noise")

        recordings.append(recording)

        # Supervision object
        supervision = SupervisionSegment(
            id=str(line_id),
            recording_id=str(line_id),
            start=0,
            duration=duration,
            channel=0,
            speaker="unknown",
            # channel_ids = [0],
            text=text,
        )
        supervisions.append(supervision)
        count += 1

    recording_set = RecordingSet.from_recordings(recordings)
    supervision_set = SupervisionSet.from_segments(supervisions)

    cuts = CutSet.from_manifests(
        recordings=recording_set,
        supervisions=supervision_set,
    )

    cuts_path = Path(args.output_file)
    cuts.to_file(cuts_path)
    logging.info(f"Written cuts to {cuts_path}")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
