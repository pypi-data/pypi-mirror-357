import json
import pickle
import re
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
import anndata as ad
import typer
from loguru import logger

from atg.utils import FeaturesDir, timeit

app = typer.Typer()


class OutputFormat(str, Enum):
    """Available output formats for processed data."""
    json = "json"
    pickle = "pickle"
    anndata = "anndata"
    csv = "csv"
    tsv = "tsv"


@dataclass
class FormatterConfig:
    """Configuration for data formatting operations."""
    
    features_dir: FeaturesDir
    class_col: int
    subclass_col: Optional[int] = None
    subject_col: Optional[int] = None
    normalization_value: float = -1.0
    output_format: OutputFormat = OutputFormat.json


class DataFormatter:
    """
    Handles formatting of input data for LEfSe analysis.
    
    Provides a complete pipeline for reading, cleaning, organizing,
    and normalizing tabular data for downstream statistical analysis.
    """
    
    def __init__(self, config: FormatterConfig):
        """Initialize formatter with configuration."""
        self.config = config
        self.raw_data: List[List[str]] = []
        self.feature_names: List[str] = []
        self.features: Dict[str, List[float]] = {}
        self.classes: Dict[str, List[str]] = {}
        self.class_slices: Dict[str, Tuple[int, int]] = {}
        self.subclass_slices: Dict[str, Tuple[int, int]] = {}
        self.class_hierarchy: Dict[str, List[str]] = {}
    
    @timeit
    def read_input_file(self, file_path: str) -> None:
        """Read tab-separated input file."""
        try:
            with open(file_path, encoding="utf-8") as file:
                self.raw_data = [
                    [value.strip() for value in line.strip().split("\t")]
                    for line in file.readlines()
                ]
            logger.info(f"Read {len(self.raw_data)} rows from {file_path}")
            
        except IOError as e:
            logger.error(f"Failed to read input file {file_path}: {e}")
            raise
    
    def _transpose_if_needed(self) -> None:
        """Transpose data matrix to ensure features are in rows for consistent processing."""
        if self.config.features_dir == FeaturesDir.cols:
            self.raw_data = list(zip(*self.raw_data))
            logger.info("Transposed data (features were in columns)")
    
    def _clean_feature_names(self, names: List[str]) -> List[str]:
        """
        Clean feature names for R compatibility and statistical analysis.
        
        R and statistical packages have strict naming requirements that prevent
        analysis failures and ensure reproducible results across platforms.
        
        Args:
            names: Raw feature names from input file
            
        Returns:
            Cleaned feature names safe for downstream analysis
        """
        # Remove characters that break R parsing and cause analysis failures
        remove_chars = [" ", "$", "@", "#", "%", "^", "&", "*", "'"]
        # Replace problematic characters to maintain readability while ensuring compatibility
        replace_chars = ["/", "(", ")", "-", "+", "=", "{", "}", "[", "]", 
                        ",", ".", ";", ":", "?", "<", ">"]
        
        cleaned = names.copy()
        
        for char in remove_chars:
            cleaned = [re.sub(re.escape(char), "", name) for name in cleaned]
        
        for char in replace_chars:
            cleaned = [re.sub(re.escape(char), "_", name) for name in cleaned]
        
        # Preserve taxonomic hierarchy structure with dots
        cleaned = [re.sub(r"\|", ".", name) for name in cleaned]
        
        # Ensure R variable name compliance to prevent parsing errors
        result = []
        for name in cleaned:
            if name and name[0] in "0123456789_":
                result.append(f"f_{name}")
            else:
                result.append(name)
        
        return result
    
    def _create_sort_key(self):
        """Create sorting function to group samples by experimental design hierarchy."""
        class_idx = self.config.class_col - 1
        subclass_idx = self.config.subclass_col - 1 if self.config.subclass_col else None
        subject_idx = self.config.subject_col - 1 if self.config.subject_col else None
        
        def sort_key(row: List[str]) -> Tuple:
            key_parts = [row[class_idx]]
            if subclass_idx is not None:
                key_parts.append(row[subclass_idx])
            if subject_idx is not None:
                key_parts.append(row[subject_idx])
            return tuple(key_parts)
        
        return sort_key
    
    def _organize_data(self) -> None:
        """
        Sort samples by experimental hierarchy for efficient slice-based analysis.
        
        LEfSe requires grouped samples to calculate within-class statistics efficiently.
        Sorting prevents expensive lookups during statistical testing phases.
        """
        self.feature_names = self._clean_feature_names(list(zip(*self.raw_data))[0])
        
        metadata_columns = list(zip(*self.raw_data))[1:]
        sort_key = self._create_sort_key()
        sorted_metadata = sorted(metadata_columns, key=sort_key)
        
        self.raw_data = list(zip(self.feature_names, *sorted_metadata))
        logger.info("Data organized by class hierarchy")
    
    def _extract_class_information(self) -> None:
        """
        Extract experimental design metadata required for statistical comparisons.
        
        LEfSe needs clear class boundaries to perform between-group comparisons
        and within-group validation for biomarker discovery.
        """
        class_idx = self.config.class_col - 1
        subclass_idx = self.config.subclass_col - 1 if self.config.subclass_col else None
        subject_idx = self.config.subject_col - 1 if self.config.subject_col else None
        
        classes = [row[class_idx + 1] for row in self.raw_data[1:]]
        
        if subclass_idx is not None:
            subclasses = [row[subclass_idx + 1] for row in self.raw_data[1:]]
        else:
            # Create default subclasses to maintain analysis structure consistency
            subclasses = [f"{cls}_subcl" for cls in classes]
        
        # Prevent ambiguous class assignments that would confound statistical tests
        subclasses = self._create_unique_subclass_names(classes, subclasses)
        
        self.classes = {"class": classes, "subclass": subclasses}
        if subject_idx is not None:
            subjects = [row[subject_idx + 1] for row in self.raw_data[1:]]
            self.classes["subject"] = subjects
        
        logger.info(f"Extracted {len(set(classes))} classes, {len(set(subclasses))} subclasses")
    
    def _create_unique_subclass_names(self, classes: List[str], subclasses: List[str]) -> List[str]:
        """
        Ensure subclass names are unique to prevent statistical test confusion.
        
        Ambiguous subclass names across different classes would lead to incorrect
        statistical groupings and invalid biomarker identification.
        """
        subclass_to_classes = {}
        for cls, subcls in zip(classes, subclasses):
            if subcls not in subclass_to_classes:
                subclass_to_classes[subcls] = set()
            subclass_to_classes[subcls].add(cls)
        
        # Identify subclasses that would cause statistical ambiguity
        conflicting = {
            subcls for subcls, cls_set in subclass_to_classes.items() 
            if len(cls_set) > 1
        }
        
        return [
            f"{cls}_{subcls}" if subcls in conflicting else subcls
            for cls, subcls in zip(classes, subclasses)
        ]
    
    def _calculate_class_slices(self) -> None:
        """
        Calculate array indices for efficient class-based statistical operations.
        
        Creates dictionaries mapping classes and subclasses to their respective
        index ranges in the data matrix. This enables efficient slicing during
        statistical testing without repeated searches.
        """
        # Create DataFrame for efficient class-based operations
        class_df = pd.DataFrame({
            'class': self.classes['class'],
            'subclass': self.classes['subclass']
        })
        
        # Initialize tracking variables
        prev_class = class_df.iloc[-1]['class']
        prev_subclass = class_df.iloc[-1]['subclass']
        subcl_slices, cl_slices, class_hrchy, subcls = [], [], [], []
        last_cl = last_subclass = 0
        
        # Calculate slices using vectorized operations where possible
        for i, (cls, subcls_val) in enumerate(zip(class_df['class'], class_df['subclass'])):
            if prev_subclass != subcls_val:
                subcl_slices.append((prev_subclass, (last_subclass, i)))
                last_subclass = i
                subcls.append(prev_subclass)
                
            if prev_class != cls:
                cl_slices.append((prev_class, (last_cl, i)))
                class_hrchy.append((prev_class, subcls))
                subcls = []
                last_cl = i
                
            prev_subclass = subcls_val
            prev_class = cls
        
        # Finalize last groups
        subcl_slices.append([prev_subclass, (last_subclass, i + 1)])
        subcls.append(prev_subclass)
        cl_slices.append([prev_class, (last_cl, i + 1)])
        class_hrchy.append((prev_class, subcls))
        
        # Store results as class attributes
        self.class_slices = dict(cl_slices)
        self.subclass_slices = dict(subcl_slices)
        self.class_hierarchy = dict(class_hrchy)
        
        logger.info(f"Calculated slices for {len(self.class_slices)} classes")
    
    def _extract_features(self) -> None:
        """
        Convert abundance data to numeric format required for statistical analysis.
        
        LEfSe statistical tests require numeric matrices, and invalid data
        would cause analysis failures or incorrect results.
        """
        # Skip metadata rows to avoid including experimental design in abundance matrix
        metadata_rows = 1
        if self.config.subclass_col is not None:
            metadata_rows += 1
        if self.config.subject_col is not None:
            metadata_rows += 1
        
        self.features = {}
        for row in self.raw_data[metadata_rows:]:
            feature_name = row[0]
            try:
                feature_values = [float(val) for val in row[1:]]
                self.features[feature_name] = feature_values
            except ValueError:
                # Skip non-numeric features to prevent downstream analysis errors
                logger.warning(f"Skipping feature {feature_name}: invalid numeric data")
                continue
        
        logger.info(f"Extracted {len(self.features)} features")
    
    def _add_missing_taxonomic_levels(self) -> None:
        """
        Generate parent-level abundances for hierarchical feature analysis.
        
        LEfSe can identify biomarkers at any taxonomic level, but missing
        intermediate levels would create gaps in biological interpretation.
        """
        if not any("." in name for name in self.features.keys()):
            return
        
        # Build taxonomy hierarchy to identify missing parent levels
        level_to_children = {}
        for feature_name in self.features.keys():
            if "." not in feature_name:
                continue
            
            parts = feature_name.split(".")
            for i in range(len(parts)):
                parent = ".".join(parts[:i]) if i > 0 else ""
                if parent and parent not in self.features:
                    if parent not in level_to_children:
                        level_to_children[parent] = []
                    level_to_children[parent].append(feature_name)
        
        # Sum child abundances to create biologically meaningful parent levels
        for parent, children in level_to_children.items():
            if parent not in self.features:
                child_values = [
                    self.features[child] for child in children 
                    if child in self.features
                ]
                if child_values:
                    self.features[parent] = [sum(values) for values in zip(*child_values)]
        
        logger.info(f"Added {len(level_to_children)} missing taxonomic levels")
    
    def _normalize_features(self) -> None:
        """
        Apply relative abundance normalization to enable cross-sample comparisons.
        
        Different sequencing depths would confound statistical comparisons,
        making normalization essential for valid biomarker discovery.
        """
        if self.config.normalization_value <= 0:
            return
        
        n_samples = len(next(iter(self.features.values())))
        feature_matrix = np.array(list(self.features.values()))
        
        # Calculate per-sample normalization to account for sequencing depth differences
        sample_totals = []
        for sample_idx in range(n_samples):
            sample_values = feature_matrix[:, sample_idx]
            total = np.sum(sample_values[sample_values > 0])
            factor = self.config.normalization_value / total if total > 0 else 0.0
            sample_totals.append(factor)
        
        for feature_name, values in self.features.items():
            normalized_values = [
                float(val) * sample_totals[i] for i, val in enumerate(values)
            ]
            
            # Handle numerical precision issues that could affect statistical tests
            mean_val = np.mean(normalized_values)
            if mean_val > 0:
                cv = np.std(normalized_values) / mean_val
                if cv < 1e-10:
                    normalized_values = [round(val * 1e6) / 1e6 for val in normalized_values]
            
            self.features[feature_name] = normalized_values
        
        logger.info(f"Normalized features to total abundance {self.config.normalization_value}")
    
    @timeit
    def process_data(self, input_file: str) -> None:
        """Execute the complete data processing pipeline."""
        logger.info("Starting data processing pipeline")
        
        self.read_input_file(input_file)
        self._transpose_if_needed()
        self._organize_data()
        self._extract_class_information()
        self._calculate_class_slices()
        self._extract_features()
        self._add_missing_taxonomic_levels()
        self._normalize_features()
        
        logger.info("Data processing pipeline completed")
    
    def get_output_data(self) -> Dict:
        """Get formatted data ready for LEfSe analysis."""
        return {
            "feats": self.features,
            "norm": self.config.normalization_value,
            "cls": self.classes,
            "class_sl": self.class_slices,
            "subclass_sl": self.subclass_slices,
            "class_hierarchy": self.class_hierarchy,
        }
    
    def _create_feature_dataframe(self) -> pd.DataFrame:
        """Create pandas DataFrame from features data."""
        # Create sample names from class information
        sample_names = [
            f"{cls}_{subcls}_{i}" 
            for i, (cls, subcls) in enumerate(zip(self.classes["class"], self.classes["subclass"]))
        ]
        
        df = pd.DataFrame(self.features, index=sample_names).T
        return df
    
    def _create_metadata_dataframe(self) -> pd.DataFrame:
        """Create metadata DataFrame for samples."""
        sample_names = [
            f"{cls}_{subcls}_{i}" 
            for i, (cls, subcls) in enumerate(zip(self.classes["class"], self.classes["subclass"]))
        ]
        
        metadata = pd.DataFrame({
            "sample_id": sample_names,
            "class": self.classes["class"],
            "subclass": self.classes["subclass"]
        })
        
        if "subject" in self.classes:
            metadata["subject"] = self.classes["subject"]
        
        metadata.set_index("sample_id", inplace=True)
        return metadata
    
    def _create_anndata_object(self) -> ad.AnnData:
        """Create AnnData object from processed data."""
        feature_df = self._create_feature_dataframe()
        metadata_df = self._create_metadata_dataframe()
        
        # AnnData expects samples as rows, features as columns
        adata = ad.AnnData(
            X=feature_df.T.values,
            obs=metadata_df,
            var=pd.DataFrame(index=feature_df.index)
        )
        
        # Add class slices and hierarchy as unstructured metadata
        adata.uns["class_slices"] = self.class_slices
        adata.uns["subclass_slices"] = self.subclass_slices
        adata.uns["class_hierarchy"] = self.class_hierarchy
        adata.uns["normalization_value"] = self.config.normalization_value
        
        return adata
    
    @timeit
    def save_output(self, output_file: str) -> None:
        """Save processed data in specified format."""
        output_path = Path(output_file)
        
        try:
            if self.config.output_format == OutputFormat.json:
                output_data = self.get_output_data()
                with output_path.open("w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved JSON output to {output_file}")
                
            elif self.config.output_format == OutputFormat.pickle:
                output_data = self.get_output_data()
                with output_path.open("wb") as f:
                    pickle.dump(output_data, f)
                logger.info(f"Saved pickle output to {output_file}")
                
            elif self.config.output_format == OutputFormat.anndata:
                adata = self._create_anndata_object()
                adata.write_h5ad(output_file)
                logger.info(f"Saved AnnData output to {output_file}")
                
            elif self.config.output_format == OutputFormat.csv:
                feature_df = self._create_feature_dataframe()
                metadata_df = self._create_metadata_dataframe()
                
                # Save feature matrix
                feature_file = output_path.with_suffix('.features.csv')
                feature_df.to_csv(feature_file)
                
                # Save metadata
                metadata_file = output_path.with_suffix('.metadata.csv')
                metadata_df.to_csv(metadata_file)
                
                logger.info(f"Saved CSV output: {feature_file}, {metadata_file}")
                
            elif self.config.output_format == OutputFormat.tsv:
                feature_df = self._create_feature_dataframe()
                metadata_df = self._create_metadata_dataframe()
                
                # Save feature matrix
                feature_file = output_path.with_suffix('.features.tsv')
                feature_df.to_csv(feature_file, sep='\t')
                
                # Save metadata  
                metadata_file = output_path.with_suffix('.metadata.tsv')
                metadata_df.to_csv(metadata_file, sep='\t')
                
                logger.info(f"Saved TSV output: {feature_file}, {metadata_file}")
                
        except IOError as e:
            logger.error(f"Failed to save output to {output_file}: {e}")
            raise


@app.command()
def format_input(
    input_file: str = typer.Option(..., "--input", "-i", help="Input tab-separated file"),
    output_file: str = typer.Option(..., "--output", "-o", help="Output file"),
    feats_dir: FeaturesDir = typer.Option("r", "--features", "-f", help="Features direction: rows (r) or cols (c)"),
    pclass: int = typer.Option(1, "--class", "-c", help="Class column number (1-indexed)"),
    psubclass: Optional[int] = typer.Option(None, "--subclass", "-s", help="Subclass column number"),
    psubject: Optional[int] = typer.Option(None, "--subject", "-u", help="Subject column number"),
    norm_v: float = typer.Option(-1.0, "--norm", "-n", help="Normalization value (-1 = no normalization)"),
    output_format: OutputFormat = typer.Option(OutputFormat.pickle, "--format", "-fmt", help="Output format: json, pickle, anndata, csv, tsv"),
):
    """Format input data for LEfSe analysis."""
    
    config = FormatterConfig(
        features_dir=feats_dir,
        class_col=pclass,
        subclass_col=psubclass,
        subject_col=psubject,
        normalization_value=norm_v,
        output_format=output_format
    )
    
    formatter = DataFormatter(config)
    formatter.process_data(input_file)
    formatter.save_output(output_file)
    
    logger.info("LEfSe data formatting completed successfully")