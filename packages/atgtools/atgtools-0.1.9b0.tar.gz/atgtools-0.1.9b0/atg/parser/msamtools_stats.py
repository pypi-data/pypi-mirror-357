import argparse
import gzip
import sys
from pathlib import Path

import pandas as pd


def read_params():
    p = argparse.ArgumentParser(
        description="Merge msamtools abundance profiles",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--input_folder", metavar="\b", required=True, help="msamtools folder results"
    )
    p.add_argument(
        "--suffix",
        metavar="\b",
        required=False,
        default="profile.abund.all.txt.gz",
        help="msamtools folder results",
    )
    p.add_argument(
        "--stats_file",
        metavar="\b",
        help="Merged output file",
        required=False,
        default="all.p95.filtered.profile.abund.stats.tsv",
    )

    p.add_argument(
        "--output_file",
        metavar="\b",
        help="Merged output file",
        required=False,
        default="all.p95.filtered.profile.abund.all.tsv",
    )

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
input_folder = Path(args.input_folder).resolve()
profiles = list(input_folder.glob(f"*{args.suffix}"))

dfs = [pd.read_table(f, comment="#") for f in profiles]
profile_abun = pd.concat(dfs, axis=1)

profile_abun.to_csv(args.output_file, sep="\t", index=False)
del profile_abun

mapstats, multimap = {}, {}

for f in profiles:
    with gzip.open(f, "rt") as file:
        lines = file.readlines()[0:8]
        sample_name = lines[7].strip()
        strings = ["Multiple mapped", "Mapped inserts"]
        match_string = [
            line.strip()
            for line in lines
            if any(x in str(line) for x in strings)  # noinspection PyTypeChecker
        ]
        mapstats.update({sample_name: match_string[0]})
        multimap.update({sample_name: match_string[1]})


results = {"mapstats": mapstats, "multimap": multimap}
msam_stats = pd.DataFrame.from_dict(results)
msam_stats.insert(
    loc=0,
    column="maprate",
    value=msam_stats["mapstats"].str.replace(r"^.*\((.*)%\)", "\\1", regex=True),
)
msam_stats["mapstats"] = msam_stats["mapstats"].str.replace(
    r"^.*\: (.*) \(.*$", "\\1", regex=True
)
msam_stats["multimap"] = msam_stats["multimap"].str.replace(
    r"^.*\((.*)%\)", "\\1", regex=True
)

msam_stats.rename_axis("ID").reset_index().to_csv(
    args.stats_file, sep="\t", index=False
)
