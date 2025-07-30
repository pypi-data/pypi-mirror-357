import argparse
import sys
from pathlib import Path

import pandas as pd


def read_params():
    p = argparse.ArgumentParser(
        description="Phylophlan results parser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--input_file", metavar="\b", required=True, help="KofamKOALA results file"
    )
    p.add_argument(
        "--output_file",
        metavar="\b",
        help="Merged output file",
        default="phylophlan_filtered_results.tsv",
    )

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
input_file = Path(args.input_file).resolve()
output_file = Path(args.output_file).resolve()

taxa = pd.read_table(input_file)
names = {0: "SGB", 1: "taxa_level", 2: "taxonomy", 3: "average_dist"}
cl = "[u|k]_[S|G|F]GBid:taxa_level:taxonomy:avg_dist"
taxa_res = pd.concat(
    [
        taxa["#input_bin"],
        taxa.iloc[:, 0:2][cl].str.split(":", expand=True).rename(names, axis="columns"),
    ],
    axis=1,
)
taxa_res.columns = taxa_res.columns.str.replace("#input_bin", "BinID")
cls = ["BinID", "SGB_status", "SGB_ID", "taxa_level", "average_dist", "taxonomy"]
tmp_res = pd.concat(
    [
        taxa_res,
        (
            taxa_res["SGB"]
            .str.replace(r"^(\w{1})", r"\1#", regex=True)
            .str.split("#", expand=True)
            .rename({0: "SGB_status", 1: "SGB_ID"}, axis=1)
        ),
    ],
    axis=1,
)[cls]
names = {
    0: "Domain",
    1: "Phylum",
    2: "Class",
    3: "Order",
    4: "Family",
    5: "Genus",
    6: "Species",
    7: "Strain",
}
phylophlan_results = pd.concat(
    [tmp_res, tmp_res["taxonomy"].str.split("|", expand=True).rename(names, axis=1)],
    axis=1,
).drop(["taxonomy", "Domain"], axis=1)

phylophlan_results[phylophlan_results["average_dist"].astype("float32") > 0.05]

phylophlan_results[
    (phylophlan_results["average_dist"].astype("float32") > 0.05)
    & (phylophlan_results["taxa_level"] == "Species")
]
# MAGs with a distance higher than 5% to the closest genome in the database can be considered as putative novel species (Manara et al., 2019; Pasolli et al., 2019).
