from typing import Dict, List, Optional, Set, Tuple, Union
import numpy as np
import pandas as pd
import pytest

from atg.div.alpha import AlphaDiversity


def test_alpha_diversity_initialization(
    sample_data: pd.DataFrame,
    invalid_data: Dict[str, Union[str, pd.DataFrame]]
) -> None:
    """Test AlphaDiversity class initialization and data validation.
    
    Args:
        sample_data: Valid sample data for testing
        invalid_data: Dictionary of invalid test datasets
    """
    alpha_div = AlphaDiversity(sample_data)
    assert isinstance(alpha_div.processed_df, pd.DataFrame)
    assert len(alpha_div.sample_names) == 5

    # Input validation ensures data integrity and prevents runtime errors
    with pytest.raises(ValueError, match="must be a pandas DataFrame"):
        AlphaDiversity(invalid_data['non_dataframe'])

    # Taxonomy column is required for species identification
    with pytest.raises(ValueError, match="Species identifier column"):
        AlphaDiversity(invalid_data['missing_taxonomy'])

    # Numeric data is required for diversity calculations
    with pytest.raises(ValueError, match="must be numeric"):
        AlphaDiversity(invalid_data['non_numeric'])

    # Negative abundances are biologically meaningless
    with pytest.raises(ValueError, match="contains negative values"):
        AlphaDiversity(invalid_data['negative_values'])


def test_alpha_diversity_grouping(sample_data_with_metadata: pd.DataFrame) -> None:
    """Test grouping functionality of AlphaDiversity.
    
    Args:
        sample_data_with_metadata: Sample data with metadata columns
    """
    # Taxonomic grouping allows analysis at different biological levels
    alpha_div = AlphaDiversity(sample_data_with_metadata, group_by_level='phylum')
    assert len(alpha_div.processed_df.columns) == 2
    assert set(alpha_div.processed_df.columns) == {'A', 'B'}


def test_diversity_indices(sample_data: pd.DataFrame) -> None:
    """Test individual diversity index calculations.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    alpha_div = AlphaDiversity(sample_data)
    sample1_data = alpha_div.normalized_abundance_matrix[0]

    # Shannon index measures both richness and evenness
    shannon_value = AlphaDiversity.shannon(sample1_data)
    assert isinstance(shannon_value, float)
    assert shannon_value > 0

    # Shannon2 allows comparison with different logarithmic bases
    shannon2_value = AlphaDiversity.shannon2(sample1_data, base=2)
    assert isinstance(shannon2_value, float)
    assert shannon2_value > 0

    # Gini-Simpson measures dominance and evenness
    gini_value = AlphaDiversity.gini(sample1_data)
    assert isinstance(gini_value, float)
    assert 0 <= gini_value <= 1

    # Simpson index measures dominance
    simpson_value = AlphaDiversity.simpson(sample1_data)
    assert isinstance(simpson_value, float)
    assert 0 <= simpson_value <= 1

    # Dominance index identifies the most abundant species
    dom_value = AlphaDiversity.dom(sample1_data)
    assert isinstance(dom_value, float)
    assert 0 <= dom_value <= 1

    # Richness counts the number of species present
    richness_value = AlphaDiversity.richness(sample1_data)
    assert isinstance(richness_value, float)
    assert richness_value >= 0

    # Pielou's evenness measures how evenly distributed the species are
    pielou_value = AlphaDiversity.pielou_e(sample1_data)
    assert isinstance(pielou_value, float)
    assert 0 <= pielou_value <= 1


def test_calculate_diversity_indices(sample_data: pd.DataFrame) -> None:
    """Test the main diversity calculation method.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    alpha_div = AlphaDiversity(sample_data)
    
    # Number equivalents convert diversity indices to effective number of species
    results = alpha_div.calculate_diversity_indices(num_equiv=True)
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 5
    assert set(results.columns) == {
        'Shannon', 'Shannon2', 'Gini-Simpson', 
        'Simpson', 'Dominance', 'Richness', 'Pielou'
    }
    
    # Raw indices provide original diversity values
    results_raw = alpha_div.calculate_diversity_indices(num_equiv=False)
    assert isinstance(results_raw, pd.DataFrame)
    assert len(results_raw) == 5


def test_edge_cases(sample_data: pd.DataFrame) -> None:
    """Test handling of edge cases.
    
    Args:
        sample_data: Sample abundance data for testing
    """
    alpha_div = AlphaDiversity(sample_data)
    results = alpha_div.calculate_diversity_indices()
    
    # Zero abundances should result in zero diversity
    assert results.loc['Sample4', 'Shannon'] == 0
    assert results.loc['Sample4', 'Richness'] == 0
    assert results.loc['Sample4', 'Pielou'] == 0

    # Single species should have maximum dominance and minimum evenness
    assert results.loc['Sample5', 'Shannon'] == 0
    assert results.loc['Sample5', 'Richness'] == 1
    assert results.loc['Sample5', 'Pielou'] == 1

    # Equal abundances should result in maximum evenness
    assert results.loc['Sample3', 'Pielou'] == 1
