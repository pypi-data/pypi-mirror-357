"""UpSet plot implementation using matplotlib/seaborn.

This module provides functionality to create UpSet plots, which are used to visualize
intersections of multiple sets. The implementation uses matplotlib and seaborn for
plotting.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


@dataclass
class UpSetConfig:
    """Configuration for UpSet plot."""
    categories_colors: List[str] = None
    categorylabel_size: int = 20
    categorylabel_color: str = 'black'
    datalabel_color: str = 'black'
    datalabel_size: int = 20
    marker_size: int = 20
    markerline_color: str = 'black'
    bar_intersect_color: str = 'black'
    figsize: tuple = (12, 8)
    
    def __post_init__(self):
        """Set default colors if not provided."""
        if self.categories_colors is None:
            self.categories_colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow']


class UpSetPlotter:
    """Class for creating UpSet plots using matplotlib/seaborn."""
    
    def __init__(self, config: Optional[UpSetConfig] = None):
        """Initialize the plotter with configuration.
        
        Args:
            config: Plot configuration parameters. If None, uses default values.
        """
        self.config = config or UpSetConfig()
        self.fig = None
        self.axes = None
        
    def _setup_figure(self) -> None:
        """Create figure and axes with proper layout."""
        self.fig = plt.figure(figsize=self.config.figsize)
        gs = self.fig.add_gridspec(1, 3, width_ratios=[0.3, 0.1, 0.6])
        
        self.axes = [
            self.fig.add_subplot(gs[0]),
            self.fig.add_subplot(gs[1]),
            self.fig.add_subplot(gs[2])
        ]
        
        plt.subplots_adjust(wspace=0.1)
        
    def _add_category_counts(self, class_counts: pd.Series) -> None:
        """Add horizontal bar chart for category counts.
        
        Args:
            class_counts: Series containing counts for each category
        """
        ax = self.axes[0]
        bars = ax.barh(
            y=class_counts.index,
            width=-class_counts.values,
            color=self.config.categories_colors[:len(class_counts)],
            height=0.4
        )
        
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width - 0.1,
                bar.get_y() + bar.get_height()/2,
                f'{abs(width):.0f}',
                ha='right',
                va='center',
                color=self.config.datalabel_color,
                size=self.config.datalabel_size
            )
            
        ax.set_xlim(1.75 * min(-class_counts.values), 0)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.invert_xaxis()
        
    def _add_category_labels(self, classes: List[str], scatter_y: List[float]) -> None:
        """Add category labels.
        
        Args:
            classes: List of category names
            scatter_y: Y-coordinates for labels
        """
        ax = self.axes[1]
        max_string_len = max(len(x) for x in classes)
        
        for i, (cls, y) in enumerate(zip(classes, scatter_y)):
            ax.text(
                -0.01 * max_string_len,
                y,
                f'<b>{cls}</b>',
                ha='center',
                va='center',
                size=self.config.categorylabel_size,
                color=self.config.categorylabel_color
            )
            
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
    def _add_intersection_matrix(self, classes: List[str], subsets: List[List[str]], 
                               scatter_x: List[int], scatter_y: List[float], max_y: float) -> None:
        """Add intersection matrix with markers and lines.
        
        Args:
            classes: List of category names
            subsets: List of subset combinations
            scatter_x: X-coordinates for markers
            scatter_y: Y-coordinates for markers
            max_y: Maximum y value for scaling
        """
        ax = self.axes[2]
        
        ax.scatter(
            scatter_x,
            scatter_y,
            s=self.config.marker_size,
            color='#C9C9C9',
            zorder=1
        )
        
        for i, subset in enumerate(subsets):
            scatter_x_has, scatter_y_has, marker_colors = [], [], []
            
            for j, cls in enumerate(classes):
                if cls in subset:
                    scatter_x_has.append(i)
                    scatter_y_has.append(-j * max_y / len(classes) - 0.1 * max_y)
                    marker_colors.append(self.config.categories_colors[j])
                    
            if scatter_x_has:
                ax.plot(
                    scatter_x_has,
                    scatter_y_has,
                    color=self.config.markerline_color,
                    linewidth=4,
                    zorder=2
                )
                
                ax.scatter(
                    scatter_x_has,
                    scatter_y_has,
                    s=self.config.marker_size,
                    color=marker_colors,
                    edgecolor=self.config.markerline_color,
                    zorder=3
                )
                
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
    def _add_intersection_bars(self, plot_df: pd.DataFrame) -> None:
        """Add vertical bars for intersection sizes.
        
        Args:
            plot_df: DataFrame containing intersection data
        """
        ax = self.axes[2]
        bars = ax.bar(
            x=range(len(plot_df)),
            height=plot_df['Size'],
            color=self.config.bar_intersect_color,
            width=0.4
        )
        
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height + 0.1,
                f'{height:.0f}',
                ha='center',
                va='bottom',
                color=self.config.datalabel_color,
                size=self.config.datalabel_size
            )
            
    def plot(self, input_file: Union[str, Path], val_col: Optional[str] = None) -> plt.Figure:
        """Create UpSet plot from CSV file.
        
        Args:
            input_file: Path to CSV file containing boolean columns
            val_col: Optional column name for weighted counts
            
        Returns:
            matplotlib Figure object
            
        Raises:
            ValueError: If no boolean columns found in DataFrame
            FileNotFoundError: If input file doesn't exist
        """
        df = pd.read_csv(input_file)
        
        classes = [x for x, y in zip(df.columns, df.dtypes) if y == bool]
        if not classes:
            raise ValueError("No boolean columns found in DataFrame")
            
        subsets = []
        for i in range(1, len(classes) + 1):
            subsets.extend([list(x) for x in itertools.combinations(classes, i)])
            
        subset_sizes = self._calculate_subset_sizes(df, classes, subsets, val_col)
        
        plot_df = pd.DataFrame({
            'Intersection': subsets,
            'Size': subset_sizes
        }).sort_values('Size', ascending=False)
        
        subsets, scatter_x, scatter_y, max_y = self._calculate_positions(classes, subsets, plot_df)
        class_counts = self._calculate_class_counts(classes, df, val_col)
        
        self._setup_figure()
        self._add_category_counts(class_counts)
        self._add_category_labels(classes, scatter_y)
        self._add_intersection_matrix(classes, subsets, scatter_x, scatter_y, max_y)
        self._add_intersection_bars(plot_df)
        
        return self.fig
        
    def _calculate_subset_sizes(self, df: pd.DataFrame, classes: List[str], 
                              subsets: List[List[str]], val_col: Optional[str]) -> List[int]:
        """Calculate sizes of each subset.
        
        Args:
            df: Input DataFrame
            classes: List of category names
            subsets: List of subset combinations
            val_col: Optional column for weighted counts
            
        Returns:
            List of subset sizes
        """
        subset_sizes = []
        for subset in subsets:
            condition = ' and '.join(
                [f"`{cls}` == True" for cls in subset] +
                [f"`{cls}` == False" for cls in classes if cls not in subset]
            )
            filtered_df = df.query(condition)
            
            if val_col is not None:
                subset_sizes.append(filtered_df[val_col].sum())
            else:
                subset_sizes.append(len(filtered_df))
                
        return subset_sizes
        
    def _calculate_positions(self, classes: List[str], subsets: List[List[str]], 
                           plot_df: pd.DataFrame) -> Tuple[List[List[str]], List[int], List[float], float]:
        """Calculate positions for plotting.
        
        Args:
            classes: List of category names
            subsets: List of subset combinations
            plot_df: DataFrame containing intersection data
            
        Returns:
            Tuple containing:
            - List of subset combinations
            - List of x-coordinates
            - List of y-coordinates
            - Maximum y value
        """
        max_y = plot_df['Size'].max() + 0.1 * plot_df['Size'].max()
        subsets = list(plot_df['Intersection'])
        
        scatter_x, scatter_y = [], []
        for i, _ in enumerate(subsets):
            for j in range(len(classes)):
                scatter_x.append(i)
                scatter_y.append(-j * max_y / len(classes) - 0.1 * max_y)
                
        return subsets, scatter_x, scatter_y, max_y
        
    def _calculate_class_counts(self, classes: List[str], df: pd.DataFrame, 
                              val_col: Optional[str]) -> pd.Series:
        """Calculate counts for each class.
        
        Args:
            classes: List of category names
            df: Input DataFrame
            val_col: Optional column for weighted counts
            
        Returns:
            Series containing class counts
        """
        sums = []
        for cls in classes:
            if val_col is not None:
                filtered_df = df[[cls, val_col]].query(f"`{cls}` == True")[val_col]
            else:
                filtered_df = df[[cls]].query(f"`{cls}` == True")[cls]
            sums.append(filtered_df.sum())
            
        return pd.Series(sums, index=classes)