#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from lhotse import RecordingSet, SupervisionSet, CutSet, Recording, SupervisionSegment
from tqdm import tqdm

from egs.liepa3.ASR.local.text_utils import clean_text, clean_tags, drop_sil


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        help="""Corpus dir.
        """,
    )
    parser.add_argument(
        "--transcript-dir",
        type=Path,
        help="""Transcript file.
        """,
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="""Output file.
            """,
    )

    parser.add_argument(
        "--audio-take-last",
        type=int,
        default="{0}_{1}.waw",
        help="""Audio file pattern.
            """,
    )

    return parser.parse_args()


class Segment():
    def __init__(self, name: str, file: str, start: float, end: float):
        self.name = name
        self.file = file
        self.start = start
        self.end = end


def main():
    args = get_args()

    logging.info(f"collecting files from {args.corpus_dir} and transcripts from {args.transcript_dir}")

    recordings = {}
    supervisions = []

    transcript_file = args.transcript_dir / "textw"
    wav_file = args.transcript_dir / "wav.scp"
    segments_file = args.transcript_dir / "segments"

    file_map = {}
    with open(wav_file, newline="", encoding="utf-8-sig") as file:
        for line in tqdm(file, desc="Processing wav.scp file"):
            line = line.strip()
            if not line:
                continue
            row = line.split(" ", maxsplit=1)
            f, str_path = row[0], row[1]
            paths = str_path.split("/")
            taken_paths = paths[-args.audio_take_last:]
            audio_path = args.corpus_dir / "/".join(taken_paths)
            logging.info(f"file: {f}, audio_path: {str(audio_path)}")
            file_map[f] = audio_path
    segments_map = {}

    with open(segments_file, newline="", encoding="utf-8-sig") as file:
        for line in tqdm(file, desc="Processing segments_file file"):
            line = line.strip()
            if not line:
                continue
            row = line.split(" ")
            if len(row) < 4:
                raise RuntimeError(f"Invalid line in segments file: {line}")
            seg, str_path, start, end = row[0], row[1], row[2], row[3]
            segments_map[seg] = Segment(name=seg, file=str_path, start=float(start), end=float(end))

    count = 0

    files = []
    with open(transcript_file, newline="", encoding="utf-8-sig") as file:
        for line_id, line in enumerate(tqdm(file, desc="Processing textw file")):
            line = line.strip()
            if not line:
                continue
            row = line.split(" ", maxsplit=1)
            if len(row) == 1:
                seg, utt_text = row[0], ""
            else:
                seg, utt_text = row[0], row[1]
            logging.info(f"segment: {seg}")
            segment = segments_map.get(seg)
            if not segment:
                logging.warning(
                    "Audio segment for '%s' not found in segments, skipping",
                    seg,
                )
                continue
            fn = file_map.get(segment.file)
            if not fn:
                logging.warning(
                    "Audio file for '%s' not found in wav.scp, skipping",
                    segment.file,
                )
                continue
            files.append((segment, fn, utt_text))
            logging.info(f"audio: {str(fn)}")

    logging.info(f"Found {len(files)} files")

    for _, (segment, fn, utt_text) in enumerate(tqdm(files, desc="Processing files")):
        audio_path = fn
        # logging.info(f"audio: {str(audio_path)}")

        # Recording object (per utterance or per file, here per utterance)
        if not audio_path or not audio_path.is_file():
            logging.warning(
                "Audio file '%s' not found, skipping",
                audio_path,
            )
            continue
        rec_id = audio_path.stem
        if rec_id not in recordings:
            recordings[rec_id] = Recording.from_file(
                audio_path,
                recording_id=rec_id
            )

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

        # Supervision object
        supervision = SupervisionSegment(
            id=segment.name,
            recording_id=rec_id,
            start=segment.start,
            duration=segment.end - segment.start,
            channel=0,
            speaker="unknown",
            # channel_ids = [0],
            text=text,
        )
        supervisions.append(supervision)
        count += 1

    recording_set = RecordingSet.from_recordings(recordings.values())
    supervision_set = SupervisionSet.from_segments(supervisions)

    cuts = CutSet.from_manifests(
        recordings=recording_set,
        supervisions=supervision_set,
    )

    if count == 0:
        raise RuntimeError("No valid files found, cannot create cuts")

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
