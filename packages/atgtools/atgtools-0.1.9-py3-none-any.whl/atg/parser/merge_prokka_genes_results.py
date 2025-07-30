import argparse
import shutil
import sys
from pathlib import Path
from typing import List, TextIO

import pyfastx
from icecream import ic


def read_params():
    p = argparse.ArgumentParser(
        description=(
            """
        Merge Prokka annotations faa and create a bed from gff files.
        """
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--prokka_out",
        help="Prokka results folder per MAG",
        metavar="\b",
        required=True,
    )
    p.add_argument(
        "--cds_outdir",
        help="The checkm output HQ filtered",
        default="CDS",
        metavar="\b",
        required=False,
    )
    p.add_argument(
        "--gff_outdir",
        help="The folder with all the MAGs",
        default="GFF",
        metavar="\b",
        required=False,
    )
    p.add_argument(
        "--mag_file",
        help="The folder with all the MAGs",
        default="MAG_genes_cds.faa",
        metavar="\b",
        required=False,
    )
    p.add_argument(
        "--bed_file",
        help="Where to put the output file",
        default="MAG_genes_cds.coord_correct.bed",
        metavar="\b",
        required=False,
    )
    p.add_argument(
        "--zero_based",
        help="If the coordinates are zero based",
        action="store_true",
        default=True,
        required=False,
    )

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    return p.parse_args()


args = read_params()
zero_based = args.zero_based

wd: Path = Path(args.prokka_out).resolve()
cds_outdir: Path = Path(args.cds_outdir).resolve()
gff_outdir: Path = Path(args.gff_outdir).resolve()
mag_file: Path = cds_outdir / args.mag_file
bed_file: Path = gff_outdir / args.bed_file

faa_files = Path(wd).glob("*/*.faa")
gff_files = Path(wd).glob("*/*.gff")
genome_files = [x for x in faa_files if not x.parent.name.startswith("CDS")]

cds_outdir.mkdir(parents=True, exist_ok=True)
gff_outdir.mkdir(parents=True, exist_ok=True)

ic(
    wd,
    cds_outdir,
    gff_outdir,
    mag_file,
    bed_file,
    zero_based,
    faa_files,
    gff_files,
    genome_files,
)

with open(mag_file, "w", encoding="utf-8") as outfile:
    for i in genome_files:
        with open(cds_outdir / f"{i.stem}.faa", "w", encoding="utf-8") as file:
            for name, seq in pyfastx.Fasta(str(i), build_index=False):
                file.write(f">{i.stem}|{name}\n{seq}\n")
        readfile: TextIO
        with open(cds_outdir / f"{i.stem}.faa", "r", encoding="utf-8") as readfile:
            shutil.copyfileobj(readfile, outfile)


def gff2bed(gff_input: str) -> List:
    with open(gff_input, encoding="utf-8") as input_file:
        result = []
        for k, v in enumerate(input_file):
            if v.startswith("gnl") and not v.startswith("#"):
                elems = v.split("\t")
                cols = {
                    "seqid": elems[0],
                    "source": elems[1],
                    "type": elems[2],
                    "start": int(elems[3]),
                    "end": int(elems[4]),
                    "score": elems[5],
                    "strand": elems[6],
                    "phase": elems[7],
                    "attributes": elems[8],
                }
                attrd = dict()
                attrs = map(lambda s: s.split("="), cols["attributes"].split(";"))
                for attr in attrs:
                    attrd[attr[0]] = attr[1]

                cols["chr"] = cols["seqid"]
                try:
                    cols["id"] = attrd["ID"]
                except KeyError:
                    cols["id"] = "."

                if zero_based:
                    if cols["start"] == cols["end"]:
                        cols["start"] -= 1
                        cols["attributes"] = ";".join(
                            [cols["attributes"], "zeroLengthInsertion=True"]
                        )
                    else:
                        cols["start"] -= 1

                result.append(cols)

        return result


with open(bed_file, "w", encoding="utf-8") as outfile:
    for i in gff_files:
        with open(gff_outdir / f"{i.stem}.bed", "w", encoding="utf-8") as file:
            for j in gff2bed(str(i)):
                j["chr"] = f"{i.stem}|{j['chr'].split('|')[2]}"
                columns = [
                    j["chr"],
                    j["start"],
                    j["end"],
                    j["id"],
                    j["score"],
                    j["strand"],
                    j["source"],
                    j["type"],
                    j["phase"],
                    j["attributes"],
                ]
                results = "\t".join(map(str, columns))
                file.write(results)
        with open(gff_outdir / f"{i.stem}.bed", "r", encoding="utf-8") as readfile:
            shutil.copyfileobj(readfile, outfile)
