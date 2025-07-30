from pathlib import Path

import typer
from multiprocessing import cpu_count

from atg.tools.ena import ena_download, ena_fields, ena_retrieve
from atg.tools.git import gitcheck
from atg.tools.manifest import create_manifest
from atg.tools.sample import subsample_fastq_seqkit
from atg.utils import OrderCommands, count_fastq, get_abundance, one_liner

tools_app = typer.Typer(
    help="Miscellaneous tools",
    cls=OrderCommands,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)


ROOT_COMMAND_HELP = """\b
Directory containing FASTQ files.
[green bold]Supported name scheme:[/green bold]\b
[green]+ sample_R1.fastq.gz[green]
[green]+ sample_R2.fastq.gz[green]
[green]+ sample_S01_R1.fastq.gz[green]
[green]+ sample_S01_R2.fastq.gz[green]
[red bold]Not supported name scheme:[/red bold]\b
[red]- sample_S01_L001_R1_001.fastq.gz[/red]
[red]- sample_S01_L001_R2_001.fastq.gz[/red]
"""

ENA_DEFAULT_PARAMS_HELP = """\b
ENA default parameters retrieved:

study_accession
sample_accession
experiment_accession
run_accession
tax_id
scientific_name
fastq_ftp
fastq_md5

"""


@tools_app.command(name="manifest")
def manifest_tools_command(
    fastq_dir: str = typer.Option(
        ..., "--fastq_dir", "-d", show_default=False, help=ROOT_COMMAND_HELP
    ),
    output_file: str = typer.Option(
        "manifest.tsv",
        "--output",
        "-o",
        show_default=False,
        help="Output file name. [default: manifest.tsv]",
    ),
    csv_format: bool = typer.Option(
        False, "--csv", "-c", help="Output CSV file format"
    ),
):
    """
    Create the manifest.[tsv/csv] file for QIIME2. [default: tsv]
    """

    create_manifest(fastq_dir=fastq_dir, output_file=output_file, csv_format=csv_format)


@tools_app.command(name="oneliner")
def oneliner_tools_command(
    input_fasta_file: str = typer.Argument(show_default=False, help="Input fasta file"),
):
    """
    Convert multiline FASTA to single line FASTA.
    """
    one_liner(input_fasta_file)


@tools_app.command(name="download")
def download_tools_command(
    bioproject: str = typer.Option(
        ..., "--bioproject", "-i", show_default=False, help="BioProject ID"
    ),
    cpus: int = typer.Option(cpu_count(), "--cpus", "-p", help="Threads"),
    fields: str = typer.Option(
        None, "--fields", "-f", show_default=False, help=ENA_DEFAULT_PARAMS_HELP
    ),
):
    """
    Download the ENA data for a given accession number.
    """
    if Path(bioproject).is_file():
        with open(bioproject, "r", encoding="utf-8") as f:
            id_samples = list(set([line.strip() for line in f]))
            for line in id_samples:
                print(line)
                ena_download(bioproject=line, cpus=cpus, fields=fields)
    else:
        ena_download(bioproject=bioproject, cpus=cpus)


@tools_app.command(name="retrieve")
def retrieve_tools_command(
    keywords: str = typer.Argument(..., help="Search query"),
    save: bool = typer.Option(False, "--save", "-s", help="Save the results to a file"),
    only_ids: bool = typer.Option(False, "--only-ids", help="Only IDs"),
):
    """
    Retrieve the ENA data for a given KEYWORDS.
    """
    ena_retrieve(keywords=keywords, save=save, only_ids=only_ids)


@tools_app.command(name="search")
def search_tools_command(
    bioproject: str = typer.Option(
        ..., "--bioproject", "-i", show_default=False, help="BioProject ID"
    ),
    save: bool = typer.Option(True, "--save", "-s", help="Save the results to a file"),
    fields: str = typer.Option(
        None, "--fields", "-f", show_default=False, help=ENA_DEFAULT_PARAMS_HELP
    ),
):
    """
    Retrieve the ENA data for a given accesion number.
    """
    ena_fields(id_err=bioproject, save=save, fields=fields)


@tools_app.command(name="git")
def git_tools_command(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", show_default=False, help="Show files & commits"
    ),
    checkremote: bool = typer.Option(
        False, "--remote", "-r", show_default=False, help="Force remote update"
    ),
    checkuntracked: bool = typer.Option(
        False, "--untracked", "-u", help="Show untracked files"
    ),
    bell_on_action_needed: bool = typer.Option(
        True, "--bell", "-b", help="Bell on action needed"
    ),
    search_dir: str = typer.Option(
        None, "--dir", "-d", help="Search <dir> for repositories"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Display info only when repository needs action"
    ),
    checkall: bool = typer.Option(
        False, "--all-branch", "-a", help="Show the status of all branches"
    ),
    show_stash: bool = typer.Option(
        False, "--stash", "-s", help="Show number of stashed changes"
    ),
):
    """
    Check multiple git repository in one pass
    """
    gitcheck(
        verbose=verbose,
        checkremote=checkremote,
        checkuntracked=checkuntracked,
        search_dir=search_dir,
        quiet=quiet,
        checkall=checkall,
        show_stash=show_stash,
    )


@tools_app.command(name="countfq")
def count_tools_command(
    input_fq: str = typer.Option(
        ...,
        "--input",
        "-i",
        show_default=False,
        help="FASTQ file or directory with FASTQ files",
    ),
    pattern: str = typer.Option(
        "--pattern", "-p", show_default=False, help="string regex pattern"
    ),
):
    """Count the number of reads in a FASTQ file"""
    count_fastq(fastq_file=input_fq, pattern=pattern)


@tools_app.command(name="abundance")
def abundance_tools_command():
    """Relative abundance tables"""
    print(get_abundance())


@tools_app.command(name="subsample")
def subsample_seqkit_tools_command(
    input_path: str = typer.Option(
        ...,
        "--input",
        "-i",
        show_default=False,
        help="FASTQ file or directory containing FASTQ files (supports both single-end and paired-end)",
    ),
    output_dir: str = typer.Option(
        ...,
        "--output",
        "-o",
        show_default=False,
        help="Output directory for subsampled files",
    ),
    proportion: float = typer.Option(
        0.1,
        "--proportion",
        "-p",
        min=0.0,
        max=1.0,
        help="Proportion of reads to subsample (0.0 to 1.0)",
    ),
    seed: int = typer.Option(
        42,
        "--seed",
        "-s",
        help="Random seed for reproducible subsampling",
    ),
    max_workers: int = typer.Option(
        cpu_count(),
        "--workers",
        "-w",
        help="Maximum number of worker threads for parallel processing",
    ),
):
    """Create subsamples of FASTQ files with specified proportion using seqkit.
    
    Supports both single-end (NAME.fastq.gz, NAME.fastq) and paired-end 
    (NAME_R1.fastq.gz/NAME_R2.fastq.gz, NAME_1.fastq.gz/NAME_2.fastq.gz) files.
    Requires seqkit to be installed.
    """
    subsample_fastq_seqkit(
        input_path=input_path,
        output_dir=output_dir,
        proportion=proportion,
        seed=seed,
        max_workers=max_workers,
    )
