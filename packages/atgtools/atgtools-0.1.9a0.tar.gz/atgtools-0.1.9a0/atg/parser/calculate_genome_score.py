import argparse
import math
import re
import sys
import time
from math import log10
from pathlib import Path

import pandas as pd
import pyfastx


def read_params():
    p = argparse.ArgumentParser(
        description=(
            """Given a folder of genomes and a checkm output it calculates the score for the genomes.
               The score can be calculated in two ways : checkm and genome [--score_method].
               The option checkm calculate the score using checkm output, while genome only on the genome quality.
            """
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument(
        "--checkm_output",
        help="The checkm output",
    )

    p.add_argument("--fasta_folder", help="The folder with all the genomes")

    p.add_argument("--output_file", help="Where to put the output file")

    p.add_argument(
        "--score_method",
        help="The score can be calculated based on checkm results [checkm] [defualt] or with a more complex formula "
        "based on the assembly [genome].\n checkm is suggested when assembly has been done only with illumina "
        "genome when assembly takes care also nanopore",
        default="checkm",
        choices=["checkm", "genome"],
    )

    p.add_argument(
        "--gap_penalty",
        help="Penalty for the number of gaps in the sequence [only if --score_method genome]",
        default=0.15,
    )

    p.add_argument(
        "--circularity_threshold",
        help="Proportion of the genome that should be captured from the a contig to be considered circular "
        "[only if --score_method genome]",
        default=0.9,
    )

    p.add_argument(
        "--favor_circular",
        help="The score in --score_method will be updated by adding the circularity fracion * number of circular "
        "bases, meaning an higher score will be given to circular genomes",
        type=bool,
        required=False,
        default=True,
    )

    return p.parse_args()


def printtime():
    return time.strftime("%H:%M:%S", time.localtime())


def is_fasta(filename: str) -> bool:
    fa = pyfastx.Fasta(filename, build_index=False)
    # pylint: disable=unused-variable
    for name, seq in fa:
        return any(seq)


def fasta_statistics_checkm_based(fasta_file: str) -> dict:
    bin_id = Path(fasta_file).stem

    print(f"[{printtime()}] Calculating statistics for {bin_id}")

    fa = pyfastx.Fasta(fasta_file, build_index=True)
    n50, l50 = fa.nl(50)
    n75, l75 = fa.nl(75)
    n90, l90 = fa.nl(90)
    contigs = len(fa)
    total = fa.size
    s_shortest = fa.shortest
    shortest_contig_size = len(s_shortest)
    shortest_contig_name = s_shortest.name
    s_longest = fa.longest
    longest_contig_size = len(s_longest)
    longest_contig_name = s_longest.name
    gc = fa.gc_content / 100
    seq_1m = fa.count(1000000)
    seq_2m = fa.count(2000000)

    info_dict = {
        "Bin_Id": bin_id,
        "Contigs": contigs,
        "Bases": total,
        "GC": round(gc, 4),
        "L50": l50,
        "L75": l75,
        "L90": l90,
        "N50_bp": n50,
        "N75_bp": n75,
        "N90_bp": n90,
        "Longest_bp": longest_contig_size,
        "Longest_contig_name": longest_contig_name,
        "Shortest_bp": shortest_contig_size,
        "Shortest_contig_name": shortest_contig_name,
        "seq_1M": seq_1m,
        "seq_2M": seq_2m,
    }

    return info_dict


def fasta_statistics_genome_based(
    fasta_file: str,
    circularity: float = 0.2,  # 0.9 default
    gap: float = 0.15,
    fcircular: bool = True,
) -> dict:
    """
    circularity : circularity_threshold
    gap : gap_penalty
    fcircular: favor_circular=True
    The function takes a fastafiles in input and calculate the statistics needed
    "Bin_Id" "Contigs" "Bases" "L50" "L75" "L90" "N50_bp" "N75_bp" "N90_bp" "Longest_bp"
    "SeqScore" "Gaps" "GapLengths" "Circular" "CircularFraction" "N1Mb" "N2Mb" "Circular_chromosome"
    """

    bin_id = Path(fasta_file).stem

    print(f"[{printtime()}] Calculating statistics for {bin_id}")

    fa = pyfastx.Fasta(fasta_file, build_index=True, full_name=True)
    contigs = len(fa)
    total = fa.size
    s_longest = fa.longest
    s_shortest = fa.shortest
    longest_contig_size = len(s_longest)
    shortest_contig_size = len(s_shortest)
    longest_contig_name = s_longest.name
    shortest_contig_name = s_shortest.name
    gc = fa.gc_content / 100
    seq_1m = fa.count(1000000)
    seq_2m = fa.count(2000000)

    length_of_contigs = [len(s.seq) for s in fa]
    number_of_gaps = 0
    total_length_of_gaps = 0

    how_many_contigs_considered_circular = 0
    name_of_circular_contigs = []
    circular_contigs_length = []
    initial_length = 0
    circular_chr = 0
    for seq in fa:
        sequence = seq.seq
        if "N" in sequence:
            total_length_of_gaps += sequence.count("N")
            # gap position: (x.start(), x.end())
            number_of_gaps += len([x for x in re.finditer("N+", sequence)])

        if "circular" in seq.name:
            c_seq_len = len(fa[seq.name].seq)
            c_seq_name = seq.name
            how_many_contigs_considered_circular += 1
            circular_contigs_length.append(c_seq_len)
            name_of_circular_contigs.append(c_seq_name)

            if c_seq_len > initial_length:
                initial_length = c_seq_len

                options = {
                    "_circularU": 3.2,
                    "_circularT": 3.15,
                    "_circularA_circularL": 3,
                    "_circularL": 2,
                }

                if c_seq_len > circularity * total:
                    for k, v in options.items():
                        if k in c_seq_name:
                            circular_chr = v
                        else:
                            circular_chr = 1

    if longest_contig_name in name_of_circular_contigs:
        longest_contig_is_circular = True
    else:
        longest_contig_is_circular = False

    # circular genome if 90% of the genome is within one contig
    circular = bool(sum(circular_contigs_length) >= (circularity * total))

    entropy = 0
    for slen in length_of_contigs:
        p = slen / total
        p_log = log10(slen / total)
        entropy -= p * p_log

    circular_fraction = sum(circular_contigs_length) / total

    n50, l50 = fa.nl(50)
    n75, l75 = fa.nl(75)
    n90, l90 = fa.nl(90)

    gscore = round(
        (
            log10(longest_contig_size)
            + log10(n90)
            - log10(total)
            - log10(l90)
            - entropy
            + (seq_1m * 0.1)
            + (seq_2m * 0.1)
            + (circular_chr * circular_fraction)
            - (gap * number_of_gaps)
        ),
        4,
    )

    if fcircular:
        gscore += round((circular_fraction * sum(circular_contigs_length)), 4)

    info_dict = {
        "Bin_Id": bin_id,
        "Contigs": contigs,
        "Bases": total,
        "GC": round(gc, 4),
        "L50": l50,
        "L75": l75,
        "L90": l90,
        "N50_bp": n50,
        "N75_bp": n75,
        "N90_bp": n90,
        "Longest_bp": longest_contig_size,
        "Longest_contig_name": longest_contig_name,
        "Longest_contig_circular": longest_contig_is_circular,
        "Shortest_bp": shortest_contig_size,
        "Shorterst_contig_name": shortest_contig_name,
        "Gaps": number_of_gaps,
        "GapLengths": total_length_of_gaps,
        "CircularContigs": name_of_circular_contigs,
        "CircularFraction": round(circular_fraction, 4),
        "Circular": circular_contigs_length,
        "ConsideredCircular": circular,
        "Score": gscore,
        "seq_1M": seq_1m,
        "seq_2M": seq_2m,
    }
    return info_dict


args = read_params()
fasta_folder = args.fasta_folder
score_method = args.score_method
gap_penalty = args.gap_penalty
circularity_threshold = args.circularity_threshold
favor_circular = args.favor_circular
path_to_checkm_table = args.checkm_output
checkm = pd.read_table(path_to_checkm_table, index_col="Bin Id")
output_file = args.output_file

exts = [".fna", ".fa", ".fasta"]
folder_fasta_file = [str(p) for p in Path(fasta_folder).iterdir() if p.suffix in exts]

print(f"Folder Fasta files: {folder_fasta_file}")
print(f"Score Method: {score_method}")

if score_method == "checkm":
    print("[calculate_score_genomes] --score_method: checkm")
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(f"#--score_method {score_method}\n")
        header_list_checkm = [
            "Bin_id",
            "Score",
            "Seq_score",
            "Qual_score",
            "Completeness",
            "Contamination",
            "Contigs",
            "Bases",
            "GC",
            "L50",
            "L75",
            "L90",
            "N50_bp",
            "N75_bp",
            "N90_bp",
            "Longest_bp",
            "Shortest_bp",
            "Strain_heterogeneity",
            "seq_1M",
            "seq_2M",
        ]
        fh.write("\t".join(header_list_checkm) + "\n")
        for file in folder_fasta_file:
            if is_fasta(file):
                genome_info = fasta_statistics_checkm_based(file)
                Path(f"{Path(file)}.fxi").unlink()
                genome_name = Path(file).stem

                print(f"[calculate_score_genomes] Score for {genome_name}")

                if genome_name in checkm.index:
                    completeness = float(checkm["Completeness"].loc[genome_name])
                    contamination = float(checkm["Contamination"].loc[genome_name])
                    strain_hetero = float(
                        checkm["Strain heterogeneity"].loc[genome_name]
                    )
                    seq_score = math.log10(
                        genome_info["Longest_bp"] / int(genome_info["Contigs"])
                    ) + math.log10(genome_info["N50_bp"] / int(genome_info["L50"]))
                    qual_score = completeness - (2 * contamination)
                    score = (0.1 * qual_score) + seq_score
                    results_list_checkm = [
                        genome_name,
                        score,
                        seq_score,
                        qual_score,
                        completeness,
                        contamination,
                        genome_info["Contigs"],
                        genome_info["Bases"],
                        genome_info["GC"],
                        genome_info["L50"],
                        genome_info["L75"],
                        genome_info["L90"],
                        genome_info["N50_bp"],
                        genome_info["N75_bp"],
                        genome_info["N90_bp"],
                        genome_info["Longest_bp"],
                        genome_info["Shortest_bp"],
                        strain_hetero,
                        genome_info["seq_1M"],
                        genome_info["seq_2M"],
                    ]
                    fh.write("\t".join(map(str, results_list_checkm)) + "\n")
                else:
                    print(
                        "There is a problem in calculate_genomes_score.py, check if the the genomes name are "
                        "identical between checkm and the dictionary in memory!"
                    )
elif score_method == "genome":
    print("[calculate_score_genomes] --score_method: genome")
    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(f"#--score_method {score_method}\n")
        header_list_genome = [
            "Bin_id",
            "Score",
            "Seq_score",
            "Qual_score",
            "Completeness",
            "Contamination",
            "Contigs",
            "Bases",
            "GC",
            "L50",
            "L75",
            "L90",
            "N50_bp",
            "N75_bp",
            "N90_bp",
            "Longest_bp",
            "Shortest_bp",
            "Gaps",
            "GapLengths",
            "CircularContigs",
            "CircularFraction",
            "Circular",
            "ConsideredCircular",
            "Strain_heterogeneity",
            "seq_1M",
            "seq_2M",
        ]
        fh.write("\t".join(map(str, header_list_genome)) + "\n")

        for file in folder_fasta_file:
            if is_fasta(file):
                genome_info = fasta_statistics_genome_based(
                    file,
                    circularity=circularity_threshold,
                    gap=gap_penalty,
                    fcircular=favor_circular,
                )
                genome_name = Path(file).stem

                if genome_name in checkm.index:
                    completeness = float(checkm["Completeness"].loc[genome_name])
                    contamination = float(checkm["Contamination"].loc[genome_name])
                    strain_hetero = float(
                        checkm["Strain heterogeneity"].loc[genome_name]
                    )

                    seq_score = float(genome_info["Score"])
                    qual_score = completeness - (2 * contamination)
                    score_checkm = (0.1 * qual_score) + seq_score
                    results_list_genome = [
                        genome_name,
                        score_checkm,
                        seq_score,
                        qual_score,
                        completeness,
                        contamination,
                        genome_info["Contigs"],
                        genome_info["Bases"],
                        genome_info["GC"],
                        genome_info["L50"],
                        genome_info["L75"],
                        genome_info["L90"],
                        genome_info["N50_bp"],
                        genome_info["N75_bp"],
                        genome_info["N90_bp"],
                        genome_info["Longest_bp"],
                        genome_info["Shortest_bp"],
                        genome_info["Gaps"],  # column added in genome modality
                        genome_info["GapLengths"],  # column added in genome modality
                        genome_info[
                            "CircularContigs"
                        ],  # column added in genome modality
                        genome_info[
                            "CircularFraction"
                        ],  # column added in genome modality
                        genome_info["Circular"],  # column added in genome modality
                        genome_info[
                            "ConsideredCircular"
                        ],  # column added in genome modality
                        strain_hetero,
                        genome_info["seq_1m"],
                        genome_info["seq_2m"],
                    ]
                    fh.write("\t".join(map(str, results_list_genome)) + "\n")
                else:
                    sys.exit(
                        "There is a problem in calculate_genomes_score.py, check if the the genomes name are "
                        "identical between checkm and the dictionary in memory!"
                    )
else:
    sys.exit("Which one did you mean? checkm or genome? Check if you type them right!")

# fasta_statistics_genome_based(str(Path.home() / "S302C354.fna"))

# TODO:
#  create score function
#  create a function to calcualate stats for each genome
#  create function for circularity
