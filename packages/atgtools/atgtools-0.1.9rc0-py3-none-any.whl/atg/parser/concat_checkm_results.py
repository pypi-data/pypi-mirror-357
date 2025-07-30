import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

parser = argparse.ArgumentParser(
    description="Concatenate checkm files and get hq bins."
)
parser.add_argument(
    "input_folder",
    metavar="INPUT",
    type=str,
    help="the input folder where the checkm files are.",
)
parser.add_argument(
    "output_folder",
    metavar="OUTPUT",
    type=str,
    help="the output folder where the checkm hq bin files will be.",
)

if len(sys.argv) == 1:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

checkm_results = Path(args.input_folder).resolve(strict=True)
output_dir = Path(args.output_folder).resolve()
output_dir.mkdir(parents=True, exist_ok=True)
checkm_files = checkm_results.glob("checkm_v*.tsv")

dfs = [pd.read_table(f, header=0) for f in checkm_files]
checkm_output = pd.concat(dfs, axis=0, ignore_index=True)
checkm_output.to_csv(output_dir / "all_checkm_results.tsv", index=False, sep="\t")
hq_checkm_results = checkm_output[
    (checkm_output["Completeness"] >= 90) & (checkm_output["Contamination"] <= 5)
]
hq_checkm_results.to_csv(output_dir / "hq_checkm_results.tsv", index=False, sep="\t")

hq_checkm_results = pd.read_csv(output_dir / "hq_checkm_results.tsv", sep="\t")
checkm_bins = checkm_results.glob("**/*fna")

for file in checkm_bins:
    for bin_id in hq_checkm_results["Bin Id"]:
        if f"{bin_id}.fna" in str(file):
            dest_file = output_dir / f"{bin_id}.fna"
            shutil.copy(file, dest_file)
