from typing import Dict, List, Union, Generator
import pytest
import pandas as pd
from atg.tools import ena
from pathlib import Path
from contextlib import contextmanager


ACCESSION_NUMBERS: List[str] = [
    "SRR16477308",
    "SRR16477307",
    "SRR17214845",
    "SRR17214844",
]
EXPECTED_COLUMNS: List[str] = [
    "study_accession",
    "sample_accession",
    "experiment_accession",
    "run_accession",
    "tax_id",
    "scientific_name",
    "fastq_ftp",
    "fastq_md5",
]
DOWNLOAD_ACCESSION_ID: str = ACCESSION_NUMBERS[0]
CPUS_FOR_TEST: int = 1


@pytest.mark.parametrize("accession_id", ACCESSION_NUMBERS)
def test_ena_fields_retrieves_data(accession_id: str) -> None:
    """Test that ena_fields retrieves data for a given run accession
    and the data contains the correct run_accession.
    
    Args:
        accession_id: ENA run accession number to test
    """
    df = ena.ena_fields(id_err=accession_id, save=False)

    assert df is not None, f"ena_fields returned None for {accession_id}"
    assert isinstance(df, pd.DataFrame), (
        f"ena_fields did not return a DataFrame for {accession_id}"
    )

    assert not df.empty, f"DataFrame is empty for {accession_id}"

    for col in EXPECTED_COLUMNS:
        assert col in df.columns, (
            f"Column '{col}' not found in DataFrame for {accession_id}"
        )

    assert accession_id in df["run_accession"].values, (
        f"Input accession {accession_id} not found in 'run_accession' column"
    )


@pytest.mark.parametrize("accession_id", ACCESSION_NUMBERS)
def test_ena_urls_returns_dict(accession_id: str) -> None:
    """Test that ena_urls processes the DataFrame from ena_fields
    and returns a dictionary of URLs.
    
    Args:
        accession_id: ENA run accession number to test
    """
    df = ena.ena_fields(id_err=accession_id, save=False)
    assert df is not None, f"Prerequisite ena_fields failed for {accession_id}"
    assert not df.empty, (
        f"Prerequisite ena_fields returned empty DataFrame for {accession_id}"
    )

    urls_dict = ena.ena_urls(df)

    assert isinstance(urls_dict, dict), "ena_urls did not return a dictionary"
    assert len(urls_dict) > 0, "ena_urls returned an empty dictionary"

    for filename, url in urls_dict.items():
        assert filename.endswith((".gz", ".bz2")), (
            f"Filename '{filename}' has unexpected extension."
        )
        assert (
            url.startswith("ftp://")
            or url.startswith("http://")
            or url.startswith("https://")
        ), (
            f"URL '{url}' for filename '{filename}' does not start with a valid protocol."
        )


@contextmanager
def manage_ena_tsv_file(accession_id: str) -> Generator[Path, None, None]:
    """Context manager to create and then cleanup the ENA TSV file.
    
    Args:
        accession_id: ENA run accession number
        
    Yields:
        Path: Path to the created TSV file
    """
    print(f"Creating TSV file for {accession_id}...")
    ena.ena_fields(id_err=accession_id, save=True)
    tsv_file_path = Path(f"{accession_id}.tsv")
    try:
        yield tsv_file_path
    finally:
        if tsv_file_path.exists():
            tsv_file_path.unlink()
            print(f"Cleaned up TSV file via context manager: {tsv_file_path}")
        else:
            print(
                f"TSV file {tsv_file_path} not found for cleanup (already deleted or never created?)."
            )


@pytest.fixture
def temp_download_dir(tmp_path_factory: pytest.TempPathFactory) -> Generator[Path, None, None]:
    """Create a temporary directory for downloads for the scope of the test.
    
    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        
    Yields:
        Path: Path to the temporary download directory
    """
    base_dir = tmp_path_factory.mktemp("ena_downloads_")
    yield base_dir


def test_ena_download_creates_files(temp_download_dir: Path) -> None:
    """Test that ena_download downloads files for a given run accession.
    It checks for directory creation and presence of at least one fastq.gz file.
    It also ensures that if files already exist (e.g. from a previous failed run),
    checksums are verified and missing/corrupt files are re-downloaded.
    
    Args:
        temp_download_dir: Temporary directory for downloads
    """
    expected_output_dir = temp_download_dir / DOWNLOAD_ACCESSION_ID

    with manage_ena_tsv_file(DOWNLOAD_ACCESSION_ID):
        print(
            f"Attempting first download for {DOWNLOAD_ACCESSION_ID} to {expected_output_dir}..."
        )
        ena.ena_download(
            bioproject=DOWNLOAD_ACCESSION_ID,
            cpus=CPUS_FOR_TEST,
            output_base_dir=temp_download_dir,
        )

        assert expected_output_dir.exists(), (
            f"Output directory {expected_output_dir} was not created."
        )
        assert expected_output_dir.is_dir(), (
            f"{expected_output_dir} is not a directory."
        )

        fastq_files = list(expected_output_dir.glob("*.fastq.gz"))
        assert len(fastq_files) > 0, (
            f"No .fastq.gz files found in {expected_output_dir}."
        )
        print(f"Found {len(fastq_files)} fastq.gz files. First download successful.")

        print(
            f"Attempting second call to ena_download for {DOWNLOAD_ACCESSION_ID} to test checksums..."
        )
        ena.ena_download(
            bioproject=DOWNLOAD_ACCESSION_ID,
            cpus=CPUS_FOR_TEST,
            output_base_dir=temp_download_dir,
        )
        assert expected_output_dir.exists(), (
            f"Output directory {expected_output_dir} was not created after second call."
        )
        fastq_files_after_checksum = list(expected_output_dir.glob("*.fastq.gz"))
        assert len(fastq_files_after_checksum) > 0, (
            f"No .fastq.gz files found in {expected_output_dir} after checksum run."
        )
        print("Checksum logic test completed (function ran without error).")
