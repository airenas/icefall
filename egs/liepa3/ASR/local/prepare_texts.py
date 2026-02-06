import argparse
import logging
import os

from lhotse import CutSet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        type=str,
        help="""Input cut file.
        """,
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="""Output txt file.
        """,
    )
    args = parser.parse_args()

    cuts = CutSet.from_file(args.input_file)

    logging.info(f"Loaded {len(cuts)} cuts")

    logging.info(f"Writing utterances to {args.output_file}")
    with open(args.output_file, "w", encoding="utf-8") as f_out:
        for cut in cuts:
            # Each cut may have one or more supervisions
            for sup in cut.supervisions:
                text = sup.text.strip()
                if text:
                    f_out.write(text + "\n")

    logging.info(f"Done writing {len(cuts)} utterances to {args.output_file}")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")

    main()

    logging.info("Done")
