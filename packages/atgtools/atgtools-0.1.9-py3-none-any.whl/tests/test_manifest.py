from typing import List, Tuple, Union
import pytest
from pathlib import Path
import pandas as pd

from atg.tools.manifest import create_manifest


@pytest.fixture
def sample_fastq_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory with dummy FASTQ files.
    
    Args:
        tmp_path: pytest fixture for creating temporary directories
        
    Returns:
        Path: Path to the temporary directory containing FASTQ files
        
    Test data structure represents real-world paired-end sequencing data:
    - Two samples with forward and reverse reads
    - Compressed format (.gz) to match production data
    - Consistent naming pattern for automated processing
    """
    fastq_data_dir = tmp_path / "fastq_data"
    fastq_data_dir.mkdir()

    samples_to_create = {
        "sampleA": ["sampleA_R1.fastq.gz", "sampleA_R2.fastq.gz"],
        "sampleB": ["sampleB_R1.fastq.gz", "sampleB_R2.fastq.gz"],
    }

    for _, file_names in samples_to_create.items():
        for fname in file_names:
            (fastq_data_dir / fname).touch()

    return fastq_data_dir


@pytest.fixture
def manifest_output_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory for manifest output.
    
    Args:
        tmp_path: pytest fixture for creating temporary directories
        
    Returns:
        Path: Path to the temporary directory for manifest output
    """
    out_dir = tmp_path / "manifest_out"
    out_dir.mkdir()
    return out_dir


@pytest.mark.parametrize(
    "csv_format, base_name, expected_ext, separator",
    [
        (False, "manifest.tsv", ".tsv", "\t"),
        (True, "manifest_for_csv.txt", ".csv", ","),
    ],
)
def test_create_manifest_formats(
    sample_fastq_dir: Path,
    manifest_output_dir: Path,
    csv_format: bool,
    base_name: str,
    expected_ext: str,
    separator: str,
) -> None:
    """Test creating manifest files in TSV and CSV formats.
    
    Args:
        sample_fastq_dir: Directory containing FASTQ files
        manifest_output_dir: Directory for manifest output
        csv_format: Whether to use CSV format
        base_name: Base name for the manifest file
        expected_ext: Expected file extension
        separator: Expected field separator
        
    Test both TSV and CSV formats to ensure compatibility with different tools:
    - TSV format for bioinformatics tools (e.g., QIIME2)
    - CSV format for general-purpose tools and spreadsheets
    """
    abs_base_output_path = manifest_output_dir / base_name

    if csv_format:
        abs_expected_final_path = abs_base_output_path.with_suffix(expected_ext)
    else:
        abs_expected_final_path = abs_base_output_path

    create_manifest(
        fastq_dir=str(sample_fastq_dir),
        output_file=str(abs_base_output_path),
        csv_format=csv_format,
    )

    # Verify file creation and naming conventions to ensure proper tool integration
    if abs_base_output_path != abs_expected_final_path:
        assert not abs_base_output_path.exists(), (
            f"Original file {abs_base_output_path} should not exist if its name/extension was changed."
        )

    assert abs_expected_final_path.exists(), (
        f"Manifest file {abs_expected_final_path} was not created."
    )

    # Verify manifest content structure to ensure downstream tool compatibility
    df = pd.read_csv(abs_expected_final_path, sep=separator)

    expected_headers = [
        "sample-id",
        "forward-absolute-filepath",
        "reverse-absolute-filepath",
    ]
    assert list(df.columns) == expected_headers, (
        f"Headers are incorrect for {expected_ext} format."
    )
    assert len(df) == 2, f"Incorrect number of samples in {expected_ext} manifest."

    # Verify file paths to ensure correct sample-to-file mapping
    for sample_id_prefix in ["sampleA", "sampleB"]:
        sample_row = df[df["sample-id"] == sample_id_prefix].iloc[0]
        assert sample_row["forward-absolute-filepath"] == str(
            sample_fastq_dir / f"{sample_id_prefix}_R1.fastq.gz"
        ), f"Forward path mismatch for {sample_id_prefix} in {expected_ext}"
        assert sample_row["reverse-absolute-filepath"] == str(
            sample_fastq_dir / f"{sample_id_prefix}_R2.fastq.gz"
        ), f"Reverse path mismatch for {sample_id_prefix} in {expected_ext}"


def test_create_manifest_empty_fastq_dir(tmp_path: Path, manifest_output_dir: Path) -> None:
    """Test that creating a manifest from an empty FASTQ directory raises FileNotFoundError.
    
    Args:
        tmp_path: pytest fixture for creating temporary directories
        manifest_output_dir: Directory for manifest output
        
    Test error handling for empty directories to prevent silent failures in production
    """
    empty_fastq_data_dir = tmp_path / "empty_fastq_data"
    empty_fastq_data_dir.mkdir()

    output_file_name = "empty_manifest.tsv"
    abs_output_path = manifest_output_dir / output_file_name

    with pytest.raises(FileNotFoundError):
        create_manifest(
            fastq_dir=str(empty_fastq_data_dir),
            output_file=str(abs_output_path),
            csv_format=False,
        )


@pytest.mark.parametrize(
    "csv_format, output_filename",
    [(False, "existing_manifest.tsv"), (True, "existing_manifest.csv")],
)
def test_create_manifest_existing_file_exits(
    sample_fastq_dir: Path,
    manifest_output_dir: Path,
    csv_format: bool,
    output_filename: str,
) -> None:
    """Test that the function raises FileExistsError if the output file already exists.
    
    Args:
        sample_fastq_dir: Directory containing FASTQ files
        manifest_output_dir: Directory for manifest output
        csv_format: Whether to use CSV format
        output_filename: Name of the output file
        
    Test error handling for existing files to prevent accidental data loss
    """
    abs_output_path = manifest_output_dir / output_filename

    abs_output_path.touch()
    assert abs_output_path.exists(), (
        f"Pre-existing file {abs_output_path} for test was not created."
    )

    with pytest.raises(FileExistsError):
        create_manifest(
            fastq_dir=str(sample_fastq_dir),
            output_file=str(abs_output_path),
            csv_format=csv_format,
        )
