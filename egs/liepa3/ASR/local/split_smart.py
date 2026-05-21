import argparse
import logging
import os
import random
from pathlib import Path
from typing import List

from lhotse import CutSet
from tqdm import tqdm


def take(cuts, max_duration: int):
    res = []
    total_duration = 0
    for i, cut in enumerate(cuts):
        if i == 0:
            logging.info(f"First cut {cut.id}")
        res.append(cut)  # make sure we add otherwise could be lost in the next iteration
        total_duration += cut.duration
        if 0 < max_duration <= total_duration:
            break
    return res


class Speaker():
    def __init__(self, speaker_id: str, gender: str, age_group: str):
        self.speaker_id = speaker_id
        self.gender = gender
        self.age_group = age_group
        self.duration = 0.0
        self.cuts = []


class Group():
    def __init__(self, gender: str, age_group: str):
        self.gender = gender
        self.age_group = age_group
        self.duration = 0.0
        self.num_cuts = 0
        self.speakers: List[Speaker] = []


def read_speakers(speakers):
    res = {}

    with open(speakers, "r") as f:
        for i, line in enumerate(tqdm(f)):
            if not line.strip():
                continue
            if i == 0:
                continue  # skip header
            strs = line.split("|")
            if len(strs) < 3:
                logging.warning(f"Invalid line in speakers file: {line}")
                continue
            speaker_id, gender, age_group = strs[0].strip(), strs[1].strip(), strs[2].strip()
            res[speaker_id] = Speaker(
                speaker_id=speaker_id,
                gender=gender,
                age_group=age_group,
            )
    return res


def select_cuts(speakers, max_duration: int):
    d, t, tr, dropped = [], [], [], 0.0
    dd, dt = 0.0, 0.0

    for i, sp in enumerate(speakers):  # index of cut, if i % 3 0 -> to test, i%3 == 1 -> to dev, else to train
        if i % 3 == 0 and dt < max_duration:
            for c in sp.cuts:
                if dt < max_duration:
                    t.append(c)
                    dt += c.duration
                elif dd < max_duration:  # otherwise to dev
                    d.append(c)
                    dd += c.duration
                else:
                    dropped += c.duration
        elif i % 3 == 1 and dd < max_duration:
            for c in sp.cuts:
                if dd < max_duration:
                    d.append(c)
                    dd += c.duration
                elif dt < max_duration:  # otherwise to test
                    t.append(c)
                    dt += c.duration
                else:
                    dropped += c.duration
        else:
            for c in sp.cuts:
                tr.append(c)
    return t, d, tr, dropped


def calc_duration(cuts_dev):
    duration = 0.0
    for cut in cuts_dev:
        duration += cut.duration
    return duration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest-dir",
        type=str,
        help="""Manifest dir.
        """,
    )
    parser.add_argument(
        "--speakers",
        type=str,
        help="""Speakers file.
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
    logging.info(f"Using speakers info from {args.speakers}")
    speakers = read_speakers(args.speakers)
    logging.info(f"Read {len(speakers)} speakers")
    groups = {}
    sp_vals = list(speakers.values())
    for s in sp_vals:
        if "?" in s.age_group or "?" in s.gender:
            del speakers[s.speaker_id]
            continue
        gr = groups.setdefault((s.gender, s.age_group), Group(s.gender, s.age_group, ))
        gr.speakers.append(s)
    groups_list = list(groups.values())
    groups_list.sort(key=lambda s: (s.gender, s.age_group), reverse=False)

    for group in groups_list:
        logging.info(
            f"Group gender: {group.gender}, age_group: {group.age_group}, duration: {group.duration / 3600:.2f} hours, num_cuts: {group.num_cuts}, num_speakers: {len(group.speakers)}")

    random.seed(42)

    manifest_path = Path(args.manifest_dir)

    logging.info(f"Loading cuts {manifest_path} ")
    cuts = CutSet.from_file(manifest_path / "cuts_all.jsonl.gz")
    found, total_duration, cl = 0, 0.0, 0
    remaining = Speaker("", "", "")
    for cut in tqdm(cuts):
        spk_id = cut.supervisions[0].speaker
        total_duration += cut.duration
        cl += 1
        if spk_id in speakers:
            sp = speakers[spk_id]
            sp.cuts.append(cut)
            sp.duration += cut.duration
            found += 1
            if (sp.gender, sp.age_group) in groups:
                group = groups[(sp.gender, sp.age_group)]
                group.duration += cut.duration
                group.num_cuts += 1
        else:
            remaining.cuts.append(cut)
            remaining.duration += cut.duration
    logging.info(
        f"Total duration {total_duration / 3600:.2f} hours in {cl} cuts")
    logging.info(
        f"Found speakers for {found} cuts, missing for {len(remaining.cuts)} cuts, total duration of missing cuts: {remaining.duration / 3600:.2f} hours")
    cuts_dev, cuts_test, cuts_train, dropped = [], [], [], 0.0
    for group in groups_list:
        group.speakers.sort(key=lambda s: s.duration, reverse=False)
        logging.info(
            f"Group gender: {group.gender}, age_group: {group.age_group}, duration: {group.duration / 3600:.2f} hours, num_cuts: {group.num_cuts}, num_speakers: {len(group.speakers)}")
        t_cuts, d_cuts, tr_cuts, drop = select_cuts(group.speakers, 3600)
        dropped += drop
        cuts_test.extend(t_cuts)
        cuts_dev.extend(d_cuts)
        cuts_train.extend(tr_cuts)
    logging.info(f"dropped speaker on test, dev: {dropped / 3600:.4f} hours")

    cuts = remaining.cuts
    random.shuffle(cuts)

    ci = iter(cuts)

    t_cuts = take(ci, 36000)  # 10h
    cuts_test.extend(t_cuts)
    d_cuts = take(ci, 36000)  # 10h
    cuts_dev.extend(d_cuts)
    tr_cuts = take(ci, 0)  # 10h
    cuts_train.extend(tr_cuts)
    logging.info(f"Dev cuts: {len(cuts_dev)}. Duration: {calc_duration(cuts_dev) / 3600:.2f} hours")
    logging.info(f"Test cuts: {len(cuts_test)}. Duration: {calc_duration(cuts_test) / 3600:.2f} hours")
    logging.info(f"Train cuts: {len(cuts_train)}. Duration: {calc_duration(cuts_train) / 3600:.2f} hours")

    cs_dev = CutSet.from_cuts(cuts_dev).shuffle()
    cs_test = CutSet.from_cuts(cuts_test).shuffle()
    cs_train = CutSet.from_cuts(cuts_train).shuffle()

    cs_test.to_file(manifest_path / "cuts_test.jsonl.gz")
    logging.info(f"Written test cuts to {manifest_path / 'cuts_test.jsonl.gz'}")
    cs_dev.to_file(manifest_path / "cuts_dev.jsonl.gz")
    logging.info(f"Written dev cuts to {manifest_path / 'cuts_dev.jsonl.gz'}")
    cs_train.to_file(manifest_path / "cuts_train.jsonl.gz")
    logging.info(f"Written train cuts to {manifest_path / 'cuts_train.jsonl.gz'}")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
