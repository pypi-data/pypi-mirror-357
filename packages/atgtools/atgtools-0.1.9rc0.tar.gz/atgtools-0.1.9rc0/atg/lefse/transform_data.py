"""Transform tabular data into tidy format for LEfSe analysis.

This module provides functionality to transform wide-format tabular data
into a tidy format suitable for LEfSe analysis, optimized for large datasets.
"""

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator
import gc

import numpy as np
import pandas as pd
from loguru import logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Transform tabular data into tidy format for LEfSe analysis"
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input tab-separated file"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Path to output file"
    )
    
    parser.add_argument(
        "--metadata-rows",
        type=int,
        default=3,
        help="Number of metadata rows at the start of the file (default: 3)"
    )
    
    parser.add_argument(
        "--format",
        choices=["csv", "tsv", "json", "pickle"],
        default="tsv",
        help="Output format (default: tsv)"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Number of rows to process at once (default: 1000)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print progress information"
    )
    
    return parser.parse_args()


class DataTransformer:
    """Transform tabular data into tidy format.
    
    This class handles the transformation of wide-format tabular data
    into a tidy format suitable for LEfSe analysis, optimized for large datasets.
    
    Attributes:
        config: Configuration parameters
        metadata: Metadata information
    """
    
    def __init__(self, config: argparse.Namespace):
        """Initialize transformer with configuration.
        
        Args:
            config: Configuration parameters
        """
        self.config = config
        self.metadata: Optional[pd.DataFrame] = None
        self.sample_names: Optional[List[str]] = None
    
    def read_metadata(self) -> None:
        """Read metadata rows from input file."""
        try:
            # Read first row to get sample names
            sample_names = pd.read_csv(
                self.config.input_file,
                sep="\t",
                nrows=1,
                header=None
            ).iloc[0, 1:].tolist()  # Skip first column (empty)
            
            self.sample_names = sample_names
            
            # Read metadata rows
            metadata_df = pd.read_csv(
                self.config.input_file,
                sep="\t",
                skiprows=1,  # Skip header row
                nrows=self.config.metadata_rows - 1,  # -1 because we already read header
                header=None,
                index_col=0
            )
            
            # Transpose to get samples as rows
            self.metadata = metadata_df.T
            self.metadata.index = sample_names
            self.metadata.index.name = "sample"
            
            # Reorder columns to put subject_id first
            if "subject_id" in self.metadata.columns:
                cols = ["subject_id"] + [col for col in self.metadata.columns if col != "subject_id"]
                self.metadata = self.metadata[cols]
            
            logger.info(f"Read metadata for {len(self.metadata)} samples")
            
        except Exception as e:
            logger.error(f"Failed to read metadata: {e}")
            raise
    
    def process_features(self) -> Iterator[pd.DataFrame]:
        """Process feature matrix in chunks.
        
        Yields:
            DataFrame chunks in tidy format
        """
        try:
            # Skip metadata rows when reading features
            for chunk in pd.read_csv(
                self.config.input_file,
                sep="\t",
                skiprows=self.config.metadata_rows + 1,  # +1 for header row
                chunksize=self.config.chunk_size,
                header=None,
                index_col=0
            ):
                # Set column names from sample names
                chunk.columns = self.sample_names
                
                # Convert to tidy format
                chunk_tidy = pd.melt(
                    chunk.reset_index().rename(columns={chunk.index.name: "feature"}),
                    id_vars=["feature"],
                    var_name="sample",
                    value_name="abundance"
                )
                
                # Convert abundance to float
                chunk_tidy["abundance"] = pd.to_numeric(chunk_tidy["abundance"], errors="coerce")
                
                # Add metadata
                chunk_tidy = chunk_tidy.merge(
                    self.metadata.reset_index(),
                    on="sample"
                )
                
                # Reorder columns: subject_id first, feature last
                if "subject_id" in chunk_tidy.columns:
                    cols = ["subject_id"] + [col for col in chunk_tidy.columns if col not in ["subject_id", "feature"]] + ["feature"]
                    chunk_tidy = chunk_tidy[cols]
                
                yield chunk_tidy
                
                # Clean up memory
                del chunk_tidy
                gc.collect()
            
        except Exception as e:
            logger.error(f"Failed to process features: {e}")
            raise
    
    def save_output(self, chunk_iterator: Iterator[pd.DataFrame]) -> None:
        """Save transformed data to file in chunks.
        
        Args:
            chunk_iterator: Iterator yielding DataFrame chunks
        """
        output_path = Path(self.config.output)
        first_chunk = True
        
        try:
            for chunk in chunk_iterator:
                if self.config.format == "csv":
                    chunk.to_csv(
                        output_path,
                        mode="w" if first_chunk else "a",
                        header=first_chunk,
                        index=False
                    )
                elif self.config.format == "tsv":
                    chunk.to_csv(
                        output_path,
                        sep="\t",
                        mode="w" if first_chunk else "a",
                        header=first_chunk,
                        index=False
                    )
                elif self.config.format == "json":
                    if first_chunk:
                        chunk.to_json(output_path, orient="records", indent=2)
                    else:
                        # Append to existing JSON array
                        with open(output_path, "r+") as f:
                            f.seek(0, 2)  # Seek to end
                            f.seek(f.tell() - 2)  # Move back before closing bracket
                            f.write(",\n" + chunk.to_json(orient="records", indent=2)[1:])
                elif self.config.format == "pickle":
                    if first_chunk:
                        chunk.to_pickle(output_path)
                    else:
                        # Append to existing pickle file
                        with open(output_path, "ab") as f:
                            chunk.to_pickle(f)
                
                first_chunk = False
                logger.info(f"Processed and saved chunk of {len(chunk)} rows")
                
                # Clean up memory
                del chunk
                gc.collect()
            
            logger.info(f"Saved all data to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            raise


def main() -> None:
    """Main function."""
    args = parse_args()
    
    if args.verbose:
        logger.add("transform.log", rotation="1 MB")
    
    transformer = DataTransformer(args)
    transformer.read_metadata()
    chunk_iterator = transformer.process_features()
    transformer.save_output(chunk_iterator)
    
    logger.info("Data transformation completed successfully")


if __name__ == "__main__":
    main() 