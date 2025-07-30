#!/usr/bin/env python

from typing import Dict, List, Union
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Creates sample abundance data for testing diversity calculations.
    
    The dataset includes various scenarios:
    - Sample1: Even distribution of abundances
    - Sample2: Two dominant species
    - Sample3: Perfectly even distribution
    - Sample4: Empty sample (all zeros)
    - Sample5: Single species dominance
    
    Returns:
        pd.DataFrame: Sample abundance data with taxonomy and sample columns
    """
    return pd.DataFrame({
        'taxonomy': ['Species1', 'Species2', 'Species3', 'Species4'],
        'Sample1': [10, 20, 30, 40],
        'Sample2': [0, 50, 0, 50],
        'Sample3': [25, 25, 25, 25],
        'Sample4': [0, 0, 0, 0],
        'Sample5': [100, 0, 0, 0]
    })


@pytest.fixture
def sample_data_with_nan() -> pd.DataFrame:
    """Creates sample data with NaN values for testing robustness.
    
    Returns:
        pd.DataFrame: Sample data with NaN values
    """
    return pd.DataFrame({
        'taxonomy': ['Species1', 'Species2', 'Species3'],
        'Sample1': [10, np.nan, 5],
        'Sample2': [15, 10, np.nan],
        'Sample3': [0, 20, 30]
    })


@pytest.fixture
def sample_data_with_metadata() -> pd.DataFrame:
    """Creates sample data with additional metadata columns for grouping tests.
    
    Returns:
        pd.DataFrame: Sample data with taxonomy, metadata, and sample columns
    """
    data = pd.DataFrame({
        'taxonomy': ['Species1', 'Species2', 'Species3', 'Species4'],
        'phylum': ['A', 'A', 'B', 'B'],
        'class': ['X', 'Y', 'X', 'Y'],
        'Sample1': [10, 20, 30, 40],
        'Sample2': [0, 50, 0, 50],
        'Sample3': [25, 25, 25, 25]
    })
    return data


@pytest.fixture
def sample_tree() -> Dict[str, Union[np.ndarray, List[np.ndarray]]]:
    """Creates a sample phylogenetic tree for UniFrac tests.
    
    Tree structure:
    Root
    ├── Branch1 (length=0.5)
    │   ├── Species1
    │   └── Species2
    └── Branch2 (length=0.3)
        ├── Species3
        └── Species4
        
    Returns:
        Dict[str, Union[np.ndarray, List[np.ndarray]]]: Tree data with branch lengths and descendants
    """
    return {
        'length': np.array([1.0, 0.5, 0.3, 0.2]),
        'descendants': [
            np.array([0, 1, 2, 3]),  # Root branch
            np.array([0, 1]),        # Left branch
            np.array([2, 3]),        # Right branch
            np.array([3])            # Terminal branch
        ]
    }


@pytest.fixture
def invalid_data() -> Dict[str, Union[str, pd.DataFrame]]:
    """Creates various invalid datasets for testing error handling.
    
    Returns:
        Dict[str, Union[str, pd.DataFrame]]: Dictionary of invalid test datasets
    """
    return {
        'non_dataframe': "not a dataframe",
        'missing_taxonomy': pd.DataFrame({
            'Sample1': [10, 20, 30],
            'Sample2': [15, 25, 35]
        }),
        'no_numeric': pd.DataFrame({
            'taxonomy': ['Species1', 'Species2'],
            'metadata': ['info1', 'info2']
        }),
        'negative_values': pd.DataFrame({
            'taxonomy': ['Species1', 'Species2'],
            'Sample1': [-1, 2],
            'Sample2': [3, -4]
        }),
        'non_numeric': pd.DataFrame({
            'taxonomy': ['Species1', 'Species2'],
            'Sample1': ['a', 'b'],
            'Sample2': ['c', 'd']
        })
    } 