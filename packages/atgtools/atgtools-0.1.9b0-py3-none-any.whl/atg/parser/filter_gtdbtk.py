import argparse
import sys
from pathlib import Path

import pandas as pd


def read_params():
    p = argparse.ArgumentParser(
        description="Parse GTDB-T output",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--input_file", metavar="\b", required=True, help="GTDB-Tk results file"
    )
    p.add_argument(
        "--output_file",
        metavar="\b",
        help="Merged output file",
        default="gtdbtk_results.tsv",
    )
    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
input_file = Path(args.input_file).resolve()
output_file = Path(args.output_file).resolve()

classification = pd.read_table(input_file, usecols=["user_genome", "classification"])

names = {
    0: "Domain",
    1: "Phylum",
    2: "Class",
    3: "Order",
    4: "Family",
    5: "Genus",
    6: "Species",
}

classify_results = (
    pd.concat(
        [
            classification["user_genome"],
            classification["classification"]
            .str.split(";", expand=True)
            .rename(names, axis=1),
        ],
        axis=1,
    )
    .rename(columns={"user_genome": "BinID"})
    .replace("^[dpcofgs]__", "", regex=True)
    .copy()
)
del classification

classify_results.to_csv(output_file, sep="\t", index=False)

# classify_results needs to be combined with mag abundance results.
