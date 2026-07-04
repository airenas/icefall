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
        "--max-test-lines",
        type=int,
        default=20000,
        help="""Maximum number of lines for the test/dev set.
        """,
    )
    parser.add_argument(
        "--max-train-words",
        type=int,
        default=2000000000,
        help="""Maximum number of words for the training set. limit to fit into int32.
        """,
    )
    parser.add_argument(
        "--output-template",
        type=str,
        help="""Output template, should contain `{}` as a placeholder for split name.
            """,
    )
    args = parser.parse_args()
    logging.info(f"Input: {args.input}")
    logging.info(f"Max test lines: {args.max_test_lines}")
    logging.info(f"Max train words: {args.max_train_words}")
    logging.info(f"Output template: {args.output_template}")
    
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

    trc, dc, tc, skip = 0, 0, 0, 0
    trw = 0

    with open(args.input, "r", encoding="utf-8") as fin, \
            open(train_f, "w", encoding="utf-8") as f_train, \
            open(dev_f, "w", encoding="utf-8") as f_dev, \
            open(test_f, "w", encoding="utf-8") as f_test:

        for line in tqdm(fin, desc="Reading file", total=total_lines):
            line = line.strip()
            if not line:
                continue

            wc = len(line.split())
            r = random.random()
            if r < train_ratio:
                if trw + wc < args.max_train_words:
                    f_train.write(line + "\n")
                    trc += 1
                    trw += wc
                else:
                    skip += 1    
            elif r < train_ratio + dev_ratio:
                if dc >= args.max_test_lines:
                    if trw + wc < args.max_train_words:
                        f_train.write(line + "\n")
                        trc += 1
                        trw += wc
                    else:
                        skip += 1    
                else:
                    f_dev.write(line + "\n")
                    dc += 1
            else:
                if tc >= args.max_test_lines:
                    if trw + wc < args.max_train_words:
                        f_train.write(line + "\n")
                        trc += 1
                        trw += wc
                    else:
                        skip += 1    
                else:
                    f_test.write(line + "\n")
                    tc += 1
    logging.info(f"Train lines: {trc}, Dev lines: {dc}, Test lines: {tc}, Skipped lines: {skip} (prevent int32 overflow)")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
