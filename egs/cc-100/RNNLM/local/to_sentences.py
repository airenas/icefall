#!/usr/bin/env python3
import argparse
import logging
import os
from typing import List

import requests
from tqdm import tqdm


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="""Input text file.
        """,
    )
    parser.add_argument(
        "--splitter-url",
        type=str,
        help="""Splittert URL (Lex URL).
        """,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="""Output file
            """,
    )

    return parser.parse_args()


MAX_CHARS = 10000


class Data:
    def __init__(self):
        self.buffer: str = ""
        self.read_lines = 0

    def append(self, line: str):
        self.buffer += line + "\n"
        self.read_lines += 1

    def take_sentences(self, s, is_last) -> List[str]:
        # print(s)
        res = []
        take_chars = 0
        for (i_from, count) in s:
            if not is_last and i_from + count > MAX_CHARS - 500:
                break
            take_chars = i_from + count
            res.append(self.buffer[i_from:i_from + count].strip())
        self.buffer = self.buffer[take_chars:]
        return res


def write_out(f_out, sentences) -> int:
    for s in sentences:
        f_out.write(s + "\n")
    return len(sentences)


def call(url: str, txt):
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, data=txt.encode("utf-8"), headers=headers, timeout=10)
    except requests.RequestException as err:
        raise RuntimeError(f"failed to send request: {err}") from err

    logging.debug("resp'%s'", resp.status_code)
    if resp.ok:
        try:
            resp_json = resp.json()
        except ValueError as err:
            raise RuntimeError(f"failed to deserialize response: {err}") from err
        return resp_json

    body_str = resp.content.decode("utf-8", errors="replace")
    raise RuntimeError(f"Failed to make request: {resp.status_code} {body_str}")


def split(url: str, data, is_last):
    txt = data.buffer
    res = call(url, txt)
    s = res.get("s", [])
    logging.debug(s)
    return data.take_sentences(s, is_last)


def main():
    args = get_args()

    logging.info(f"splitting to sentences {args.input}")

    data = Data()
    wrote = 0

    with open(args.output, "w", encoding="utf-8") as f_out:
        with open(args.input, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc="Reading file"):
                line = line.rstrip("\n")
                data.append(line)

                # If single line is bigger than MAX_CHARS → flush first
                if len(data.buffer) > MAX_CHARS:
                    sentences = split(args.splitter_url, data, False)
                    wrote += write_out(f_out, sentences)

            # send remaining data
            if data.buffer:
                sentences = split(args.splitter_url, data, True)
                wrote += write_out(f_out, sentences)
        logging.info(f"read {data.read_lines}, wrote {wrote} sentences")


if __name__ == "__main__":
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=formatter,
                        level=getattr(logging, os.environ.get("LOGLEVEL", "WARNING").upper(), logging.WARNING))

    logging.info(f"Starting")
    main()
    logging.info(f"Done")
