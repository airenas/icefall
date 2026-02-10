import argparse
import logging
import os
import random

from tqdm import tqdm


def count_lines(fn: str):
    res = 0
    with open(fn, "r", encoding="utf-8") as f:
        for _ in tqdm(f, desc="Reading file"):
            res += 1
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="""Input text file.
        """,
    )
    parser.add_argument(
        "--output-template",
        type=str,
        help="""Output template, should contain `{}` as a placeholder for split name.
            """,
    )
    args = parser.parse_args()

    random.seed(42)

    total_lines = count_lines(args.input)
    logging.info(f"Total lines: {total_lines}")
    if args.output_template.count("{}") != 1:
        raise ValueError("Output template should contain exactly one {} placeholder")
    train_f = args.output_template.replace("{}", "train")
    dev_f = args.output_template.replace("{}", "dev")
    test_f = args.output_template.replace("{}", "test")

    train_ratio = 0.9
    dev_ratio = 0.05

    trc, dc, tc = 0, 0, 0

    with open(args.input, "r", encoding="utf-8") as fin, \
            open(train_f, "w", encoding="utf-8") as f_train, \
            open(dev_f, "w", encoding="utf-8") as f_dev, \
            open(test_f, "w", encoding="utf-8") as f_test:

        for line in tqdm(fin, desc="Reading file", total=total_lines):
            line = line.strip()
            if not line:
                continue

            r = random.random()
            if r < train_ratio:
                f_train.write(line + "\n")
                trc += 1
            elif r < train_ratio + dev_ratio:
                f_dev.write(line + "\n")
                dc += 1
            else:
                f_test.write(line + "\n")
                tc += 1
    logging.info(f"Train lines: {trc}, Dev lines: {dc}, Test lines: {tc}")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
