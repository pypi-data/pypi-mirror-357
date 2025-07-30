"""Simplified LEfSe implementation using pingouin/scikit-learn.

This module provides a streamlined implementation of LEfSe (Linear discriminant analysis
Effect Size) for biomarker discovery, using Python-native statistical libraries.
"""

import math
import pickle
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path

import numpy as np
import pandas as pd
import pingouin as pg
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import typer
from loguru import logger


@dataclass
class LefseData:
    """Data class for LEfSe input data.
    
    Attributes:
        features: Dictionary mapping feature names to feature values
        classes: Dictionary mapping class names to class labels
        class_slices: Dictionary mapping class names to slice indices
        subclass_slices: Dictionary mapping subclass names to slice indices
        class_hierarchy: Dictionary mapping class names to lists of subclass names
        normalization_value: Value used for normalization
    """
    features: Dict[str, List[float]]
    classes: Dict[str, List[str]]
    class_slices: Dict[str, Tuple[int, int]]
    subclass_slices: Dict[str, Tuple[int, int]]
    class_hierarchy: Dict[str, List[str]]
    normalization_value: float


@dataclass
class LefseResults:
    """Data class for LEfSe results.
    
    Attributes:
        class_means: Dictionary mapping feature names to class means
        class_names: List of class names
        lda_scores: Dictionary mapping feature names to LDA scores
        lda_scores_thresholded: Dictionary mapping feature names to thresholded LDA scores
        wilcoxon_results: Dictionary mapping feature names to Wilcoxon test results
    """
    class_means: Dict[str, List[float]]
    class_names: List[str]
    lda_scores: Dict[str, float]
    lda_scores_thresholded: Dict[str, float]
    wilcoxon_results: Dict[str, str]


class LefseAnalyzer:
    """LEfSe analysis implementation.
    
    This class implements the LEfSe (Linear discriminant analysis Effect Size)
    algorithm for biomarker discovery.
    
    Attributes:
        data: LefseData object containing input data
        results: LefseResults object containing analysis results
    """
    
    def __init__(self, data: LefseData):
        """Initialize LEfSe analyzer.
        
        Args:
            data: LefseData object containing input data
        """
        self.data = data
        self.results = None
        self._feature_df = None
        self._metadata_df = None
        self._prepare_dataframes()
    
    def _prepare_dataframes(self) -> None:
        """Prepare pandas DataFrames for efficient analysis."""
        # Create feature matrix
        self._feature_df = pd.DataFrame(self.data.features).T
        
        # Create metadata DataFrame
        self._metadata_df = pd.DataFrame({
            'class': self.data.classes['class'],
            'subclass': self.data.classes['subclass']
        })
        
        if 'subject' in self.data.classes:
            self._metadata_df['subject'] = self.data.classes['subject']
    
    def get_class_means(self) -> Tuple[List[str], Dict[str, List[float]]]:
        """Calculate mean values for each class using pandas.
        
        Returns:
            Tuple of (class names, dictionary of class means per feature)
        """
        class_names = list(self.data.class_slices.keys())
        means = {}
        
        for feat_name in self._feature_df.index:
            feat_values = self._feature_df.loc[feat_name]
            class_means = []
            
            for cls in class_names:
                start, end = self.data.class_slices[cls]
                class_means.append(feat_values.iloc[start:end].mean())
            
            means[feat_name] = class_means
        
        return class_names, means
    
    def kruskal_wallis_test(self, feature_values: pd.Series, 
                           class_labels: pd.Series, 
                           alpha: float = 0.05) -> Tuple[bool, float]:
        """Perform Kruskal-Wallis H-test using pingouin.
        
        Args:
            feature_values: Series of feature values
            class_labels: Series of corresponding class labels
            alpha: Significance threshold
            
        Returns:
            Tuple of (is_significant, p_value)
        """
        df = pd.DataFrame({
            'value': feature_values,
            'group': class_labels
        })
        
        stats = pg.kruskal_anova(dv='value', between='group', data=df)
        p_value = stats.loc[0, 'p-unc']
        
        return p_value < alpha, p_value
    
    def wilcoxon_test(self, feature_values: pd.Series, 
                     class_labels: pd.Series, 
                     alpha: float = 0.05) -> Tuple[bool, float]:
        """Perform Mann-Whitney U test using pingouin.
        
        Args:
            feature_values: Series of feature values
            class_labels: Series of corresponding class labels
            alpha: Significance threshold
            
        Returns:
            Tuple of (is_significant, p_value)
        """
        classes = sorted(set(class_labels))
        if len(classes) != 2:
            raise ValueError("Wilcoxon test requires exactly 2 classes")
        
        stats = pg.mwu(
            feature_values[class_labels == classes[0]],
            feature_values[class_labels == classes[1]]
        )
        p_value = stats.loc['MWU', 'p-val']
        
        return p_value < alpha, p_value
    
    def lda_analysis(self, features: pd.DataFrame, 
                    class_labels: pd.Series, 
                    n_boots: int = 30,
                    sample_frac: float = 0.8,
                    lda_threshold: float = 2.0) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Perform Linear Discriminant Analysis with bootstrapping.
        
        Args:
            features: DataFrame of feature values
            class_labels: Series of class labels
            n_boots: Number of bootstrap iterations
            sample_frac: Fraction of samples to use in each bootstrap
            lda_threshold: Threshold for LDA scores
            
        Returns:
            Tuple of (lda_scores, thresholded_scores)
        """
        X = features.values
        y = class_labels.values
        feature_names = features.index
        
        scores = {name: [] for name in feature_names}
        
        for _ in range(n_boots):
            n_samples = int(len(X) * sample_frac)
            indices = np.random.choice(len(X), size=n_samples, replace=False)
            X_boot = X[indices]
            y_boot = y[indices]
            
            lda = LinearDiscriminantAnalysis()
            lda.fit(X_boot, y_boot)
            
            w = lda.coef_[0]
            w_unit = w / np.sqrt(np.sum(w**2))
            ld_scores = X_boot @ w_unit
            
            class_means = {c: np.mean(ld_scores[y_boot == c]) for c in lda.classes_}
            effect_size = abs(class_means[lda.classes_[0]] - class_means[lda.classes_[1]])
            
            for i, name in enumerate(feature_names):
                scores[name].append(abs(w_unit[i] * effect_size))
        
        final_scores = {}
        for name in feature_names:
            mean_score = np.mean(scores[name])
            final_scores[name] = math.copysign(1.0, mean_score) * math.log(1.0 + abs(mean_score), 10)
        
        thresholded_scores = {k: v for k, v in final_scores.items() if abs(v) > lda_threshold}
        
        return final_scores, thresholded_scores
    
    def analyze(self, anova_alpha: float = 0.05,
               wilcoxon_alpha: float = 0.05,
               lda_threshold: float = 2.0,
               n_boots: int = 30,
               sample_frac: float = 0.8,
               verbose: bool = False) -> LefseResults:
        """Run LEfSe analysis.
        
        Args:
            anova_alpha: Significance threshold for Kruskal-Wallis test
            wilcoxon_alpha: Significance threshold for Wilcoxon test
            lda_threshold: Threshold for LDA scores
            n_boots: Number of bootstrap iterations
            sample_frac: Fraction of samples to use in each bootstrap
            verbose: Whether to print progress information
            
        Returns:
            LefseResults object containing analysis results
        """
        class_names, class_means = self.get_class_means()
        wilcoxon_results = {}
        significant_features = {}
        
        for feat_name in self._feature_df.index:
            if verbose:
                logger.info(f"Testing feature: {feat_name}")
            
            feat_values = self._feature_df.loc[feat_name]
            class_labels = self._metadata_df['class']
            
            kw_significant, kw_pvalue = self.kruskal_wallis_test(
                feat_values, 
                class_labels, 
                anova_alpha
            )
            
            if not kw_significant:
                if verbose:
                    logger.info(f"\tKruskal-Wallis test not significant (p={kw_pvalue:.3f})")
                wilcoxon_results[feat_name] = "-"
                continue
            
            if verbose:
                logger.info(f"\tKruskal-Wallis test significant (p={kw_pvalue:.3f})")
            
            wilcoxon_significant, wilcoxon_pvalue = self.wilcoxon_test(
                feat_values,
                class_labels,
                wilcoxon_alpha
            )
            
            if wilcoxon_significant:
                significant_features[feat_name] = feat_values
                wilcoxon_results[feat_name] = f"{wilcoxon_pvalue:.3f}"
                if verbose:
                    logger.info(f"\tWilcoxon test significant (p={wilcoxon_pvalue:.3f})")
            else:
                wilcoxon_results[feat_name] = "-"
                if verbose:
                    logger.info(f"\tWilcoxon test not significant (p={wilcoxon_pvalue:.3f})")
        
        if significant_features:
            significant_df = pd.DataFrame(significant_features).T
            lda_scores, lda_scores_thresholded = self.lda_analysis(
                significant_df,
                self._metadata_df['class'],
                n_boots,
                sample_frac,
                lda_threshold
            )
        else:
            lda_scores = {}
            lda_scores_thresholded = {}
        
        self.results = LefseResults(
            class_means=class_means,
            class_names=class_names,
            lda_scores=lda_scores,
            lda_scores_thresholded=lda_scores_thresholded,
            wilcoxon_results=wilcoxon_results
        )
        
        if verbose:
            logger.info(f"\nNumber of significant features: {len(significant_features)}")
            logger.info(f"Number of features with LDA score > {lda_threshold}: "
                       f"{len(lda_scores_thresholded)}")
        
        return self.results
    
    def save_results(self, output_file: str) -> None:
        """Save results to file.
        
        Args:
            output_file: Path to output file
        """
        if not self.results:
            raise ValueError("No results to save. Run analyze() first.")
            
        with open(output_file, "w", encoding="utf-8") as out:
            for feat_name, feat_means in self.results.class_means.items():
                out.write(f"{feat_name}\t{math.log(max(max(feat_means), 1.0), 10.0)}\t")
                
                if feat_name in self.results.lda_scores_thresholded:
                    max_class_idx = np.argmax(feat_means)
                    out.write(f"{self.results.class_names[max_class_idx]}\t")
                    out.write(f"{self.results.lda_scores[feat_name]}")
                else:
                    out.write("\t")
                    
                wilcoxon_p = self.results.wilcoxon_results.get(feat_name, "-")
                out.write(f"\t{wilcoxon_p}\n")


def load_data(input_file: str) -> LefseData:
    """Load data from pickle file.
    
    Args:
        input_file: Path to input pickle file
        
    Returns:
        LefseData object containing input data
    """
    with open(input_file, "rb") as inputf:
        inp = pickle.load(inputf)
    return LefseData(
        features=inp["feats"],
        classes=inp["cls"],
        class_slices=inp["class_sl"],
        subclass_slices=inp["subclass_sl"],
        class_hierarchy=inp["class_hierarchy"],
        normalization_value=inp.get("norm", -1.0)
    )


app = typer.Typer()


@app.command()
def run_lefse(
    input_file: str = typer.Option(..., "--input", "-i", help="Input file"),
    output_file: str = typer.Option(..., "--output", "-o", help="Output file"),
    anova_alpha: float = typer.Option(0.05, "--anova", "-a", help="Significance threshold for Kruskal-Wallis test"),
    wilcoxon_alpha: float = typer.Option(0.05, "--wilcoxon", "-w", help="Significance threshold for Wilcoxon test"),
    lda_threshold: float = typer.Option(2.0, "--lda", "-l", help="Threshold for LDA scores"),
    n_boots: int = typer.Option(30, "--boots", "-b", help="Number of bootstrap iterations"),
    sample_frac: float = typer.Option(0.8, "--sample", "-s", help="Fraction of samples to use in each bootstrap"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print progress information"),
) -> None:
    """Run LEfSe analysis.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        anova_alpha: Significance threshold for Kruskal-Wallis test
        wilcoxon_alpha: Significance threshold for Wilcoxon test
        lda_threshold: Threshold for LDA scores
        n_boots: Number of bootstrap iterations
        sample_frac: Fraction of samples to use in each bootstrap
        verbose: Whether to print progress information
    """
    logger.info("Starting LEfSe analysis")
    
    data = load_data(input_file)
    analyzer = LefseAnalyzer(data)
    analyzer.analyze(
        anova_alpha=anova_alpha,
        wilcoxon_alpha=wilcoxon_alpha,
        lda_threshold=lda_threshold,
        n_boots=n_boots,
        sample_frac=sample_frac,
        verbose=verbose
    )
    analyzer.save_results(output_file)
    
    logger.info("LEfSe analysis completed successfully")


if __name__ == "__main__":
    app() 