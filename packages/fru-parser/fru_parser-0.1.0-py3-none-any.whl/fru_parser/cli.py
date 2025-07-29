
import logging
import sys
import argparse
from .parser import parse_fru
def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fru-bin", default="fru.bin", help="path of input FRU binary file"
    )
    parser.add_argument("--output", default="fru.json", help="path of output json file")
    args = parser.parse_args()
    fru_bin = args.fru_bin
    # Check if the file exists
    try:
        with open(fru_bin, "rb") as f:
            pass
    except FileNotFoundError:
        logging.error(f"File {fru_bin} not found.")
        sys.exit(1)
    output_json_path = args.output
    parse_fru(fru_bin, output_json_path)