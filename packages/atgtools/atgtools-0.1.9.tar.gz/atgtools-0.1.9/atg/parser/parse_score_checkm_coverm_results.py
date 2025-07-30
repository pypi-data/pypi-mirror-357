import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd


def read_params():
    p = argparse.ArgumentParser(
        description=(
            """
        Parse CheckM and CoverM results, moves HQ MAGs to a new folder, "HQ_MAGs" folder, by default.
        """
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--score_table", help="The score output file", required=True)
    p.add_argument(
        "--coverm_output", help="The checkm output HQ filtered", required=True
    )
    p.add_argument("--mags", help="The folder with all the MAGs", required=True)
    p.add_argument(
        "--output_folder",
        help="The folder with all the MAGs",
        default="HQ_MAGS",
        required=True,
    )
    p.add_argument(
        "--output_file",
        help="Where to put the output file",
        default="coverm_unique_cluster_scored.tsv",
        required=True,
    )

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
score_table = args.score_table
coverm_clusters = args.coverm_output
genomes_folders = args.mags
output_folder = args.output_folder
output_file = args.output_file

score_table = pd.read_table(score_table, comment="#")
coverm_table = pd.read_table(coverm_clusters, names=["ref_cluster", "cluster_members"])

clusters = coverm_table.apply(
    lambda x: x.str.replace(r"^.*\/(.*)\.f.*$", "\\1"), regex=True, axis=1
)
unique_ids = list(clusters["ref_cluster"].unique())

dfs = []

print("Getting the scores for the clusters")

for x in unique_ids:
    clusters_id = clusters[clusters["ref_cluster"] == x]
    members = clusters_id["cluster_members"].to_list()
    scores = score_table[score_table["Bin_id"].isin(members)]
    top_score = scores.sort_values(by=["Score"], ascending=False)
    dfs.append(top_score.reset_index(drop=True).loc[0])

df = pd.concat(dfs, axis=1).T.reset_index(drop=True)

Path(output_folder).mkdir(parents=True, exist_ok=True)

df.to_csv(output_file, sep="\t", index=False)

best_unique_genomes = df["Bin_id"].to_list()

for genome in best_unique_genomes:
    print(f"Copying {genome}.fna to {output_folder}")
    shutil.copy(f"{genomes_folders}/{genome}.fna", f"{output_folder}/{genome}.fna")

"""
python parse_scores_checkm_coverm_results.py \
    --score_table 06_hq_checkm/score_checkm_results.tsv \
    --coverm_output 07_coverm/coverm_unique_clusters.tsv \
    --mags 06_hq_checkm/ \
    --output_folder 08_hq_nr_mags \
    --output_file 08_hq_nr_mags/score_checkm_results.tsv


executable="/home/projects/ku_00042/apps/miniconda3/bin/python3"
nohup ${executable} python calculate_genome_score.py \
    --checkm_output 06_hq_checkm/hq_checkm_results.tsv \
    --fasta_folder 06_hq_checkm \
    --output_file TEST_score_checkm_results.tsv \
    --score_method checkm &> scored.log & 

for i in $(< best_unique_genomes.txt )
do
    echo $i
    rsync -a 06_hq_checkm/${i}.fna 08_hq_nr_mags/
done
"""
