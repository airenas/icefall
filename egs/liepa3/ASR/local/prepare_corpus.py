#!/usr/bin/env python3
import argparse
import csv
import logging
import os
from pathlib import Path

from lhotse import RecordingSet, SupervisionSet, CutSet, Recording, SupervisionSegment


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
        "--output-dir",
        type=str,
        help="""Output dir.
            """,
    )

    parser.add_argument(
        "--limit-count",
        type=int,
        default=0,
        help="""How many items to take.
            if 0 then take all
            used for test run
                """,
    )

    return parser.parse_args()


def clean(param: str) -> str:
    """Clean the input text.
    """

    # remove punctuations
    res = "".join(c if c.isalnum() or c.isspace() else " " for c in param)
    # remove double spaces
    return " ".join(res.split()).casefold()


def main():
    args = get_args()

    logging.info(f"collecting files from {args.corpus_dir}")
    if args.limit_count > 0:
        logging.warning(f"TEST MODE: collecting max {args.limit_count} files")

    recordings = []
    supervisions = []

    corpus_dir = Path(args.corpus_dir)
    transcript_file = Path(args.transcript_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0

    with open(transcript_file, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            audio_rel_path = Path(row["Audio_file_path_title"])
            audio_path = corpus_dir / audio_rel_path
            recording_id = row.get("Record_id")
            if not recording_id:
                logging.warning(f"No Record_id {row}")
                continue
            if not audio_path.is_file():
                logging.warning(f"file not found: {audio_path}")
                continue

            speaker = row["Speaker_id"]
            duration = float(row["Duration_total"]) / 1000.0
            start_sec = float(row["Utterance_start"]) / 1000.0  # CSV is in ms
            text = clean(row["Utterance_text"])

            # Recording object (per utterance or per file, here per utterance)
            recording = Recording.from_file(audio_path, recording_id=recording_id)
            recordings.append(recording)

            # Supervision object
            supervision = SupervisionSegment(
                id=recording_id,
                recording_id=recording_id,
                start=start_sec,
                duration=duration,
                channel=0,
                speaker=speaker,
                text=text,
            )
            supervisions.append(supervision)
            count += 1
            if args.limit_count > 0 and count >= args.limit_count:
                logging.warning(f"collected : {count}")
                break

    recording_set = RecordingSet.from_recordings(recordings)
    supervision_set = SupervisionSet.from_segments(supervisions)

    cuts = CutSet.from_manifests(
        recordings=recording_set,
        supervisions=supervision_set,
    )

    cuts_path = output_dir / "cuts_all.jsonl.gz"
    cuts.to_file(cuts_path)
    print(f"Written cuts to {cuts_path}")

    logging.info("done")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
