import argparse
import sys
from pathlib import Path

import pandas as pd
import pyfastx

wd = Path.home() / "Documents/Sandbox"
# bed_file = wd / "NIX/GFF/MAG_genes_cds.1.bed"
# faa_file = wd / "NIX/CDS/MAG_genes_cds.faa"
dir_out = wd / "NIX"
# file_name = "MAG_genes_cds"


def read_params():
    p = argparse.ArgumentParser(
        description="Parse Kofam, InterProScan, eggNOG and dbCAN results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--bed_file", metavar="\b", required=True, help="KofamKOALA results file"
    )
    p.add_argument("--faa_file", metavar="\b", required=True, help="dbCAN results file")
    p.add_argument(
        "--output_file",
        metavar="\b",
        help="Merged output file",
        default="annotation_results.tsv",
    )

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
bed_file = Path(args.bed_file).resolve()
faa_file = Path(args.faa_file).resolve()
file_name = args.output_file

bed_cls = [
    "chr",
    "start",
    "stop",
    "name",
    "score",
    "strand",
    "source",
    "feature",
    "frame",
    "info",
]
genome_df = pd.read_table(bed_file, header=None, names=bed_cls)

genome_df["coord"] = genome_df[["chr", "start", "stop"]].apply(
    lambda x: "_".join(map(str, x)), axis=1
)

genome_df[["genome", "contig"]] = (
    genome_df["chr"]
    .str.split("|", expand=True)
    .rename(columns={0: "genome", 1: "contig"})
)

genome_df["name2"] = genome_df["name"]
genome_df["ID_gene"] = genome_df[["genome", "name2"]].apply("|".join, axis=1)
dot_id = genome_df[genome_df["name"] == "."]
genome_df.loc[dot_id.index, "ID_gene"] = (
    dot_id["chr"] + "|" + dot_id["start"].astype(str) + "_" + dot_id["stop"].astype(str)
)

genome_df["name"] = genome_df["name2"]
genome_df["info"] = genome_df["ID_gene"]
genome_sub_df = genome_df[bed_cls].copy()

genome_sub_df.to_csv(dir_out / f"GFF/{file_name}py.bed", sep="\t", index=False)
genome_sub = genome_df[["coord", "name", "source", "feature"]]
genome_sub = genome_sub.sort_values("source").reset_index(drop=True).copy()
genome_sub_dplyr = (
    genome_df.groupby("coord")
    .agg(
        {
            "coord": "first",
            "name": lambda x: ";".join(x.unique()),
            "source": lambda x: ",".join(x.unique()),
            "feature": lambda x: "|".join(x.unique()),
        }
    )
    .reset_index(drop=True)
)

genome_sub2 = genome_df[["coord", "chr", "start", "stop"]].copy()
genome_sub2_u = genome_sub2[~genome_sub2["coord"].duplicated()].reset_index(drop=True)
genome_df_u = pd.merge(genome_sub2_u, genome_sub_dplyr, on="coord")
genome_sub_df = genome_df_u.copy()
genome_sub_df[["score", "frame"]] = "."
genome_sub_df[["genome", "contig"]] = (
    genome_sub_df["chr"]
    .str.split("|", expand=True)
    .rename(columns={0: "genome", 1: "contig"})
)

dot_id = genome_sub_df[genome_sub_df["name"] == "."]
genome_sub_df.loc[dot_id.index, "name"] = (
    dot_id["contig"]
    + "_"
    + dot_id["start"].astype(str)
    + "_"
    + dot_id["stop"].astype(str)
)

genome_sub_df["name2"] = genome_sub_df["name"].str.split(";", expand=True)[0]
genome_sub_df["info"] = genome_sub_df["genome"] + "|" + genome_sub_df["name2"]
genome_sub_df["strand"] = "."

genome_sub_df2 = genome_sub_df[bed_cls].copy()
genome_sub_df2.to_csv(
    dir_out / f"{file_name}_SUBSETpy.bed", sep="\t", index=False, header=False
)

genome_sub_df2["coord"] = (
    genome_sub_df2["chr"]
    + "_"
    + genome_sub_df2["start"].astype(str)
    + "_"
    + genome_sub_df2["stop"].astype(str)
)

genome_sub_df2["coord"] = genome_sub_df2["coord"].str.replace("-", "_", regex=True)
genome_sub_df2["source2"] = genome_sub_df2["source"].str.split(",").str[0]

fasta_MAGgenes = pyfastx.Fasta(str(faa_file), build_index=True)

fa_given_names = [x.name for x in fasta_MAGgenes]
fa_given_seqs = [x.seq for x in fasta_MAGgenes]

fastafile_genes = pd.DataFrame({"ID": fa_given_names, "seq": fa_given_seqs})

fastafile_genes_sub = fastafile_genes[
    fastafile_genes["ID"].isin(
        genome_sub_df2[
            ~genome_sub_df2["source2"].isin(
                ["macrel", "gutsmash_PBGC", "antismash_SBGC"]
            )
        ]["info"]
    )
].copy()
# TODO: define output filename and replace dir_out
#   refactoring
with open(dir_out / f"{file_name}_translated_SUBSETpy.faa", "w") as file:
    for k, v in enumerate(fastafile_genes_sub["seq"]):
        file.write(f">{fastafile_genes_sub.loc[k][0]}\n{v}\n")
