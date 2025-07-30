#!/usr/bin/env python

from typing import Dict, List, Union
import pytest
import numpy as np
import pandas as pd
from atg.div.beta import BetaDiversity


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Creates sample abundance data for testing.
    
    Returns:
        pd.DataFrame: Sample abundance data with taxonomy and sample columns
    """
    data = {
        'taxonomy': ['Species1', 'Species2', 'Species3', 'Species4'],
        'Sample1': [10, 20, 0, 5],
        'Sample2': [15, 10, 5, 0],
        'Sample3': [0, 0, 30, 10],
        'Sample4': [10, 20, 0, 5],  # Identical to Sample1
        'Sample5': [100, 0, 0, 0]   # Single species dominance
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_tree() -> Dict[str, Union[np.ndarray, List[np.ndarray]]]:
    """Creates a sample phylogenetic tree for UniFrac tests.
    
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


def test_init_validation(
    sample_data: pd.DataFrame,
    invalid_data: Dict[str, Union[str, pd.DataFrame]]
) -> None:
    """Tests initialization validation.
    
    Args:
        sample_data: Valid sample data for testing
        invalid_data: Dictionary of invalid test datasets
    """
    # Test with invalid input type
    with pytest.raises(ValueError, match="must be a pandas DataFrame"):
        BetaDiversity(invalid_data['non_dataframe'])
    
    # Test with missing taxonomy column
    with pytest.raises(ValueError, match="Species identifier column"):
        BetaDiversity(invalid_data['missing_taxonomy'])
    
    # Test with no numeric columns
    with pytest.raises(ValueError):
        BetaDiversity(invalid_data['no_numeric'])


def test_data_processing(sample_data: pd.DataFrame) -> None:
    """Tests data processing and normalization.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    beta = BetaDiversity(sample_data)
    
    # Verify data structure and dimensions
    assert beta.processed_df.shape == (5, 4)  # 5 samples, 4 species
    
    # Verify sample and species names are correctly extracted
    assert set(beta.sample_names) == {'Sample1', 'Sample2', 'Sample3', 'Sample4', 'Sample5'}
    assert set(beta.species_names) == {'Species1', 'Species2', 'Species3', 'Species4'}
    
    # Verify abundances are properly normalized to proportions
    assert np.allclose(beta.normalized_abundance_matrix.sum(axis=1), 1.0)


def test_euclidean_distance(sample_data: pd.DataFrame) -> None:
    """Tests Euclidean distance calculations.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    # Test Euclidean distance properties:
    # - Measures absolute differences in species abundances
    # - Should be symmetric and have zero diagonal
    # - Should handle NaN values appropriately
    beta = BetaDiversity(sample_data)
    distances = beta.calculate_pairwise_distances('euclidean')
    
    # Verify distance matrix properties
    assert distances.shape == (5, 5)
    assert np.allclose(distances, distances.T, equal_nan=True)
    assert np.all(np.diag(distances) == 0)
    
    # Verify distance calculations
    assert distances.loc['Sample1', 'Sample1'] == 0
    assert distances.loc['Sample1', 'Sample2'] > 0
    assert distances.loc['Sample1', 'Sample3'] > 0


def test_braycurtis_distance(sample_data: pd.DataFrame) -> None:
    """Tests Bray-Curtis distance calculations.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    # Test Bray-Curtis distance properties:
    # - Measures relative differences in species abundances
    # - Should be symmetric and have zero diagonal
    # - Should be bounded between 0 and 1
    beta = BetaDiversity(sample_data)
    distances = beta.calculate_pairwise_distances('braycurtis')
    
    # Verify distance matrix properties
    assert distances.shape == (5, 5)
    assert np.allclose(distances, distances.T, equal_nan=True)
    assert np.all(np.diag(distances) == 0)
    
    # Verify distance calculations
    assert distances.loc['Sample1', 'Sample1'] == 0
    
    # Verify distance range
    assert np.allclose(distances >= 0, True, equal_nan=True)
    assert np.allclose(distances <= 1, True, equal_nan=True)


def test_jensenshannon_distance(sample_data: pd.DataFrame) -> None:
    """Tests Jensen-Shannon divergence calculations.
    
    Args:
        sample_data: Sample abundance data for testing
        
    The Jensen-Shannon divergence should:
    - Be symmetric (JS(x,y) = JS(y,x))
    - Have zero diagonal (JS(x,x) = 0)
    - Be bounded between 0 and 1
    - Handle edge cases properly:
      * Return 1.0 for zero-sum distributions
      * Return 0.0 for identical distributions
      * Handle zero probabilities correctly
    """
    beta = BetaDiversity(sample_data)
    distances = beta.calculate_pairwise_distances('jensenshannon')
    
    # Verify distance matrix properties
    assert distances.shape == (5, 5)
    assert np.allclose(distances, distances.T, equal_nan=True)
    assert np.all(np.diag(distances) == 0)
    
    # Verify distance calculations
    assert distances.loc['Sample1', 'Sample1'] == 0  # Self-comparison
    assert distances.loc['Sample1', 'Sample4'] == 0  # Identical samples
    
    # Verify distance range
    assert np.allclose(distances >= 0, True, equal_nan=True)
    assert np.allclose(distances <= 1, True, equal_nan=True)
    
    # Test edge cases
    zero_vector = np.zeros_like(sample_data.iloc[0, 1:])
    non_zero_vector = np.ones_like(sample_data.iloc[0, 1:])
    
    # Test zero vs non-zero
    assert beta.jensenshannon(zero_vector, non_zero_vector) == 1.0
    assert beta.jensenshannon(non_zero_vector, zero_vector) == 1.0
    
    # Test identical vectors
    assert beta.jensenshannon(non_zero_vector, non_zero_vector) == 0.0


def test_jaccard_distance(sample_data: pd.DataFrame) -> None:
    """Tests Jaccard distance calculations.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    # Test Jaccard distance properties:
    # - Measures presence/absence differences
    # - Should be symmetric and have zero diagonal
    # - Should be bounded between 0 and 1
    beta = BetaDiversity(sample_data)
    distances = beta.calculate_pairwise_distances('jaccard')
    
    # Verify distance matrix properties
    assert distances.shape == (5, 5)
    assert np.allclose(distances, distances.T, equal_nan=True)
    assert np.all(np.diag(distances) == 0)
    
    # Verify distance calculations
    assert distances.loc['Sample1', 'Sample1'] == 0
    
    # Verify distance range
    assert np.allclose(distances >= 0, True, equal_nan=True)
    assert np.allclose(distances <= 1, True, equal_nan=True)


def test_unifrac_distances(
    sample_data: pd.DataFrame,
    sample_tree: Dict[str, Union[np.ndarray, List[np.ndarray]]]
) -> None:
    """Tests both weighted and unweighted UniFrac distances.
    
    Args:
        sample_data: Sample abundance data for testing
        sample_tree: Phylogenetic tree data for UniFrac calculations
    """
    beta = BetaDiversity(sample_data)
    
    # Test weighted UniFrac
    weighted_distances = beta.calculate_pairwise_distances('unifrac')
    assert weighted_distances.shape == (5, 5)
    assert np.allclose(weighted_distances, weighted_distances.T, equal_nan=True)
    assert np.all(np.diag(weighted_distances) == 0)
    
    # Test unweighted UniFrac
    unweighted_distances = beta.calculate_pairwise_distances('unweighted_unifrac')
    assert unweighted_distances.shape == (5, 5)
    assert np.allclose(unweighted_distances, unweighted_distances.T, equal_nan=True)
    assert np.all(np.diag(unweighted_distances) == 0)


def test_nan_handling(sample_data_with_nan: pd.DataFrame) -> None:
    """Tests handling of NaN values in input data.
    
    Args:
        sample_data_with_nan: Sample data containing NaN values
    """
    # Test that NaN values in input data are properly handled:
    # - NaN values should be excluded from distance calculations
    # - Resulting distance matrix should be symmetric
    # - Diagonal should be zero
    beta = BetaDiversity(sample_data_with_nan)
    distances = beta.calculate_pairwise_distances('euclidean')
    
    # Verify calculations work with NaN values
    assert not np.isnan(distances.values).any()
    assert distances.shape == (3, 3)
    
    # Verify matrix properties with NaN handling
    assert np.allclose(distances.values, distances.values.T, equal_nan=True)
    assert np.all(np.diag(distances.values) == 0)


def test_calculate_all_distances(sample_data: pd.DataFrame) -> None:
    """Tests calculation of all distance metrics.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    beta = BetaDiversity(sample_data)
    all_distances = beta.calculate_all_distances()
    
    # Verify all metrics are present
    expected_metrics = {
        'euclidean', 'braycurtis', 'jensenshannon',
        'jaccard', 'unifrac', 'unweighted_unifrac'
    }
    assert set(all_distances.keys()) == expected_metrics
    
    # Verify each distance matrix
    for metric, distances in all_distances.items():
        assert distances.shape == (5, 5)
        assert np.allclose(distances, distances.T, equal_nan=True)
        assert np.all(np.diag(distances) == 0)


def test_invalid_metric(sample_data: pd.DataFrame) -> None:
    """Tests handling of invalid metric names.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    beta = BetaDiversity(sample_data)
    with pytest.raises(ValueError, match="Invalid metric"):
        beta.calculate_pairwise_distances('invalid_metric') 