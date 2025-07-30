import argparse
import sys
from functools import partial, reduce
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from rich import print
from tqdm import tqdm

# from icecream import ic
# ic.configureOutput(prefix='-> ')


def read_params():
    p = argparse.ArgumentParser(
        description="Parse Kofam, InterProScan, eggNOG and dbCAN results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--kofam_result", metavar="\b", required=True, help="KofamKOALA results file"
    )
    p.add_argument(
        "--dbcan_result", metavar="\b", required=True, help="dbCAN results file"
    )
    p.add_argument(
        "--eggnog_result", metavar="\b", required=True, help="eggNOG results file"
    )
    p.add_argument(
        "--interpro_result",
        metavar="\b",
        required=True,
        help="InterProScan results file",
    )
    p.add_argument(
        "---omit_intermediate_files",
        action="store_false",
        required=False,
        help="InterProScan results file",
    )
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


def dbcan_output(
    dbcan_result: str, output_dir: Path, to_file: bool = True
) -> pd.DataFrame:
    chunksize = 10**6

    dbcan = pd.concat(
        [
            chunk
            for chunk in tqdm(
                pd.read_table(Path(dbcan_result).resolve(), chunksize=chunksize),
                desc="Loading data",
            )
        ]
    )

    # dbcan = pd.read_table(Path(dbcan_result).resolve())
    dbcan.drop("#ofTools", axis=1, inplace=True)
    dbcan.columns = dbcan.columns.str.replace("Gene ", "")

    can = dbcan.apply(
        lambda x: x.str.replace(r"\(.*?\)", "", regex=True)
        .str.replace("+", ",", regex=True)
        .str.replace("-", ""),
        axis=1,
    ).copy()

    del dbcan

    can["data"] = (
        can[can.columns[1:]]
        .apply(lambda x: ",".join(x), axis=1)
        .str.replace(",$", "", regex=True)
    )

    results: Dict[str, Dict[Any, Any]] = dict(dbCAN_mod={}, dbCAN_enzclass={})
    dbc = can.set_index("ID").loc[:, "data"].copy()
    for k, v in enumerate(dbc):
        canmod = []
        enzclass = []
        for i in list(set(v.split(","))):
            if "CBM" in i:
                canmod.append(i)
            elif len(i):
                enzclass.append(i)

        results["dbCAN_mod"][dbc.index[k]] = ",".join(canmod)
        results["dbCAN_enzclass"][dbc.index[k]] = ",".join(enzclass)

    res = pd.DataFrame.from_dict(results).replace("", "-")
    res.index = res.index.rename("ID")
    res.sort_values("ID").reset_index(drop=True, inplace=True)

    if to_file:
        dbcan_out_dir = output_dir / "dbCAN"
        dbcan_out_dir.mkdir(parents=True, exist_ok=True)
        dbcan_file = dbcan_out_dir / "dbcan_results.tsv"
        res.reset_index("ID").to_csv(dbcan_file, sep="\t", index=False)
        print(f"[bold cyan]Output dbCAN results to:[/] {dbcan_file}")
    return res


def kofam_output(
    kofam_result: str, output_dir: Path, to_file: bool = True
) -> pd.DataFrame:
    chunksize = 10**6
    kofam = pd.concat(
        list(
            tqdm(
                pd.read_table(
                    Path(kofam_result).resolve(),
                    names=["ID", "kofam_KO"],
                    chunksize=chunksize,
                ),
                desc="Loading data",
            )
        )
    )
    # kofam = pd.read_table(Path(kofam_result).resolve(), names=["ID", "kofam_KO"])
    kofam_filtered = (
        kofam.dropna().groupby("ID").agg({"kofam_KO": ",".join}).reset_index()
    )

    del kofam

    # kofam_filtered.replace(";K", ",K", regex=True, inplace=True)
    kofam_filtered.sort_values("ID").reset_index(drop=True, inplace=True)

    if to_file:
        kofam_out_dir = output_dir / "Kofam"
        kofam_out_dir.mkdir(parents=True, exist_ok=True)
        kofam_file = kofam_out_dir / "kofam_results.tsv"
        kofam_filtered.to_csv(kofam_file, sep="\t", index=False)
        print(f"[bold cyan]Output Kofam results to:[/] {kofam_file}")
    return kofam_filtered


def eggnog_output(
    eggnog_result: str, output_dir: Path, to_file: bool = True
) -> pd.DataFrame:
    chunksize = 10**6
    eggnog = pd.concat(
        list(
            tqdm(
                pd.read_table(Path(eggnog_result).resolve(), chunksize=chunksize),
                desc="Loading data",
            )
        )
    )

    # eggnog = pd.read_table(Path(eggnog_result).resolve())

    cls = ["#query", "eggNOG_OGs", "KEGG_ko", "KEGG_Pathway", "KEGG_Module", "PFAMs"]
    en = eggnog[cls].copy()
    del eggnog
    en.columns = en.columns.str.replace("#query", "ID", regex=True)
    en["KEGG_ko"] = en["KEGG_ko"].str.replace("ko:", "", regex=True)

    filtered: Dict[Any, str] = {}
    egg = en["eggNOG_OGs"].str.replace(r"\|\w+,", ",", regex=True).copy()

    for k, v in egg.to_dict().items():
        filtered[k] = ",".join([x for x in v.split(",") if x.endswith("@1")])

    en["eggNOG_OGs"] = filtered.values()
    en["eggNOG_OGs"] = en["eggNOG_OGs"].str.replace("@1", "", regex=True)
    en.sort_values("ID").reset_index(drop=True, inplace=True)

    if to_file:
        eggnog_out_dir = output_dir / "eggNOG"
        eggnog_out_dir.mkdir(parents=True, exist_ok=True)
        eggnog_file = eggnog_out_dir / "eggnog_results.tsv"
        en.to_csv(eggnog_file, sep="\t", index=False)
        print(f"[bold cyan]Output eggNOG results to:[/] {eggnog_file}")
    return en


def interpro_output(
    interpro_result: str, output_dir: Path, to_file: bool = True
) -> pd.DataFrame:
    cols = [
        "ID",
        "md5",
        "length",
        "analysis",
        "signature_accession",
        "signature_description",
        "Start",
        "Stop",
        "score",
        "Status",
        "date",
        "interpro_id",
        "description",
        "interpro_GO",
        "interpro_PWY",
    ]
    fields = ["ID", "interpro_id", "description", "interpro_GO", "interpro_PWY"]
    chunksize = 10**6

    # chunk = pd.read_table(interpro_result, names=cols, na_values='-', chunksize=chunksize)
    # df = pd.concat(chunk)
    df = pd.concat(
        list(
            tqdm(
                pd.read_table(
                    interpro_result, names=cols, na_values="-", chunksize=chunksize
                ),
                desc="Loading data",
            )
        )
    )

    ipres = (
        df[df["interpro_id"].notna()][fields]
        .sort_values("ID")
        .reset_index(drop=True)
        .copy()
    )

    del df

    ipres["interpro_info"] = ipres[["interpro_id", "description"]].apply(
        lambda x: ": ".join(x), axis=1
    )

    interpro = (
        ipres.groupby("ID")
        .agg(
            {
                "interpro_info": "|".join,
                "interpro_id": "|".join,
                "interpro_GO": lambda x: ";".join(x.dropna()),
                # "interpro_PWY": lambda x: '#'.join(x.dropna())
            }
        )
        .reset_index()
        .copy()
    )

    # rep = ['interpro_id', 'interpro_GO', 'interpro_PWY']
    rep = ["interpro_id", "interpro_GO"]
    interpro[rep] = interpro[rep].applymap(lambda x: ",".join(set(x.split("#"))))
    interpro.sort_values("ID").reset_index(drop=True, inplace=True)
    interpro["interpro_GO"] = (
        interpro["interpro_GO"].replace(r"^s*$", float("NaN"), regex=True).fillna("-")
    )

    if to_file:
        ipres_out_dir = output_dir / "InterPro"
        ipres_out_dir.mkdir(parents=True, exist_ok=True)
        ipres_file = ipres_out_dir / "interpro_results.tsv"
        interpro.to_csv(ipres_file, sep="\t", index=False)
        print(f"[bold cyan]Output InterPro results to:[/] {ipres_file}")

    return interpro


if __name__ == "__main__":
    args = read_params()
    output_file = Path(args.output_file).resolve()
    output_folder = output_file.parents[0] / "annotations"
    write_inter = args.omit_intermediate_files

    print("[bold magenta]Reading Kofam results")
    kofamdf = kofam_output(args.kofam_result, output_folder, to_file=write_inter)

    print("[bold magenta]Reading dbCAN results")
    dbcandf = dbcan_output(args.dbcan_result, output_folder, to_file=write_inter)

    print("[bold magenta]Reading eggNOG results")
    eggnogdf = eggnog_output(args.eggnog_result, output_folder, to_file=write_inter)

    print("[bold magenta]Reading InterPro results")
    interprodf = interpro_output(
        args.interpro_result, output_folder, to_file=write_inter
    )

    print("[bold magenta]Merging results")
    dfs_list = [dbcandf, kofamdf, eggnogdf, interprodf]
    dfs = reduce(partial(pd.merge, on="ID", how="outer"), dfs_list)  # type: ignore
    annotation_results = dfs.fillna("-").sort_values("ID").reset_index(drop=True).copy()
    annotation_results.to_csv(output_file, sep="\t", index=False)
