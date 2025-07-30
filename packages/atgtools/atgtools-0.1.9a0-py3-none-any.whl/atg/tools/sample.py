import subprocess
import shutil
from pathlib import Path
from typing import Tuple

from loguru import logger
from atg.utils import check_paired, fastq_files, thread_map_parallel



def _get_output_suffix(input_file: Path) -> str:
    """Get output filename suffix based on input file extension."""
    suffix = input_file.suffix
    if suffix == '.gz':
        return '.fastq.gz'
    elif suffix in ['.fastq', '.fq']:
        return '.fastq'
    else:
        return '.fastq'

def check_seqkit_installed() -> bool:
    """Check if seqkit is installed and available."""
    return shutil.which("seqkit") is not None


def _subsample_single_seqkit(args: Tuple[str, str, str, float, int]) -> None:
    """Subsample a single-end FASTQ file using seqkit."""
    input_file, output_dir, sample_name, proportion, seed = args
    input_file = Path(input_file)
    output_dir = Path(output_dir)
    
    output_suffix = _get_output_suffix(input_file)
    output_file = output_dir / f"{sample_name}_subsample{output_suffix}"
    
    cmd = [
        "seqkit", "sample", str(input_file),
        "-p", str(proportion),
        "--rand-seed", str(seed),
        "-o", str(output_file)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)


def _subsample_paired_seqkit(args: Tuple[str, str, str, str, float, int]) -> None:
    """Subsample paired-end FASTQ files using seqkit."""
    r1_file, r2_file, output_dir, sample_name, proportion, seed = args
    r1_file = Path(r1_file)
    r2_file = Path(r2_file)
    output_dir = Path(output_dir)
    
    output_suffix = _get_output_suffix(r1_file)
    r1_output = output_dir / f"{sample_name}_R1_subsample{output_suffix}"
    r2_output = output_dir / f"{sample_name}_R2_subsample{output_suffix}"
    
    # Subsample R1
    cmd_r1 = [
        "seqkit", "sample", str(r1_file),
        "-p", str(proportion),
        "--rand-seed", str(seed),
        "-o", str(r1_output)
    ]
    
    # Subsample R2 with same seed for paired consistency
    cmd_r2 = [
        "seqkit", "sample", str(r2_file),
        "-p", str(proportion),
        "--rand-seed", str(seed),
        "-o", str(r2_output)
    ]
    
    subprocess.run(cmd_r1, check=True, capture_output=True)
    subprocess.run(cmd_r2, check=True, capture_output=True)


def subsample_fastq_seqkit(
    input_path: str,
    output_dir: str,
    max_workers: int,
    proportion: float = 0.1,
    seed: int = 42,
    pattern: str = r".*(_([1-2]|R[1-2])\.(fastq|fq)\.gz$|\.(fastq|fq)(\.gz)?$)",
) -> None:
    """Create subsamples of FASTQ files using seqkit.
    
    Supports both single-end and paired-end FASTQ files:
    - Single-end: NAME.fastq.gz, NAME.fastq, NAME.fq.gz, NAME.fq
    - Paired-end: NAME_R1.fastq.gz/NAME_R2.fastq.gz, NAME_1.fastq.gz/NAME_2.fastq.gz
    
    Args:
        input_path: Path to FASTQ file or directory containing FASTQ files
        output_dir: Output directory for subsampled files
        proportion: Proportion of reads to subsample (0.0 to 1.0)
        seed: Random seed for reproducible subsampling
        pattern: Regex pattern to match FASTQ files
        max_workers: Maximum number of worker threads for parallel processing
    """
    if not check_seqkit_installed():
        raise RuntimeError("seqkit is not installed. Please install seqkit first.")
    
    if not 0.0 < proportion <= 1.0:
        raise ValueError("Proportion must be between 0.0 and 1.0")
    
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fastq_dict = fastq_files(str(input_path), pattern)
    if not fastq_dict:
        raise FileNotFoundError(f"No FASTQ files found in {input_path}")
    
    file_types = check_paired(fastq_dict)
    logger.info(f"Found {len(file_types['paired'])} paired-end samples, {len(file_types['single'])} single-end samples")
    
    if file_types['single']:
        single_args = []
        for sample_name, file_path in file_types['single'].items():
            single_args.append((str(file_path), str(output_dir), sample_name, proportion, seed))
        
        thread_map_parallel(_subsample_single_seqkit, single_args, max_workers)
    
    if file_types['paired']:
        paired_args = []
        for sample_name, pair_dict in file_types['paired'].items():
            paired_args.append((
                str(pair_dict['R1']), 
                str(pair_dict['R2']), 
                str(output_dir), 
                sample_name, 
                proportion, 
                seed
            ))
        
        thread_map_parallel(_subsample_paired_seqkit, paired_args, max_workers) 