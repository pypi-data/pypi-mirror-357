"""Venn diagram implementation using matplotlib.

This module provides functionality to create Venn diagrams, which are used to visualize
set intersections. The implementation uses matplotlib and matplotlib-venn for plotting.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib_venn import venn3, venn3_circles


@dataclass
class VennConfig:
    """Configuration for Venn diagram."""
    set_labels: Tuple[str, str, str] = ("Set A", "Set B", "Set C")
    alpha: float = 0.75
    colors: List[str] = None
    figsize: Tuple[int, int] = (8, 8)
    label_size: int = 12
    label_weight: str = "bold"
    
    def __post_init__(self):
        """Set default colors if not provided."""
        if self.colors is None:
            self.colors = ["#ff1164ff", "#ffb500ff", "#4b9179ff"]


class VennPlotter:
    """Class for creating Venn diagrams using matplotlib."""
    
    def __init__(self, config: Optional[VennConfig] = None):
        """Initialize the plotter with configuration.
        
        Args:
            config: Plot configuration parameters. If None, uses default values.
        """
        self.config = config or VennConfig()
        self.fig = None
        self.ax = None
        self._mixed_colors = {}
        
    def _setup_figure(self):
        """Create figure and set style."""
        self.fig = plt.figure(figsize=self.config.figsize)
        
        plt.rcParams["legend.fancybox"] = False
        plt.rcParams["legend.framealpha"] = 1
        plt.rcParams["legend.edgecolor"] = "1"
        plt.rcParams["legend.facecolor"] = "white"
        plt.rcParams["axes.facecolor"] = "#f1ece0ff"
        
        plt.rcParams["axes.spines.right"] = False
        plt.rcParams["axes.spines.top"] = False
        plt.rcParams["axes.spines.bottom"] = False
        plt.rcParams["axes.spines.left"] = False
        
    def _calculate_mixed_colors(self) -> None:
        """Calculate mixed colors for intersections."""
        def set_mix(*cols):
            self._mixed_colors[frozenset(cols[:-1])] = cols[-1]
            
        set_mix(self.config.colors[0], self.config.colors[1], "#ff6332ff")
        set_mix(self.config.colors[1], self.config.colors[2], "#a5a33cff")
        set_mix(self.config.colors[0], self.config.colors[2], "#a5516eff")
        set_mix(self.config.colors[0], self.config.colors[1], self.config.colors[2], "#c3724aff")
        
    def _get_mixed_color(self, *cols):
        """Get mixed color for given colors.
        
        Args:
            *cols: Colors to mix
            
        Returns:
            Mixed color
        """
        return self._mixed_colors[frozenset(cols)]
        
    def _create_venn(self, sets: List[Set]):
        """Create Venn diagram.
        
        Args:
            sets: List of three sets to plot
        """
        venn = venn3(
            subsets=sets,
            set_labels=self.config.set_labels,
            subset_label_formatter=None,
            alpha=self.config.alpha
        )
        
        venn3_circles(subsets=sets, lw=1.2, color="white")
        
        venn.get_patch_by_id("100").set_color(self.config.colors[0])
        venn.get_patch_by_id("010").set_color(self.config.colors[1])
        venn.get_patch_by_id("001").set_color(self.config.colors[2])
        
        venn.get_patch_by_id("110").set_color(self._get_mixed_color(self.config.colors[0], self.config.colors[1]))
        venn.get_patch_by_id("011").set_color(self._get_mixed_color(self.config.colors[1], self.config.colors[2]))
        venn.get_patch_by_id("101").set_color(self._get_mixed_color(self.config.colors[0], self.config.colors[2]))
        venn.get_patch_by_id("111").set_color(self._get_mixed_color(*self.config.colors))
        
        ids = ["{:{fill}3b}".format(c, fill="0") for c in range(1, 8)]
        values = [int(venn.get_label_by_id(_id).get_text()) for _id in ids]
        min_value, max_value = min(values), max(values)
        min_size, max_size = 12, 20
        
        for _id, value in zip(ids, values):
            venn.get_patch_by_id(_id).set_edgecolor("none")
            size = min_size + (max_size - min_size) * ((value - min_value) / max_value)
            venn.get_label_by_id(_id).set_fontsize(size)
            
        return venn
        
    def plot(self, data: Union[pd.DataFrame, List[Set]], save: Optional[Union[bool, str]] = False) -> plt.Figure:
        """Create Venn diagram from data.
        
        Args:
            data: DataFrame with three columns or list of three sets
            save: Whether to save the plot. If string, save to that path.
            
        Returns:
            matplotlib Figure object
            
        Raises:
            ValueError: If data is invalid
        """
        if isinstance(data, pd.DataFrame):
            if len(data.columns) != 3:
                raise ValueError("DataFrame must have exactly 3 columns")
            sets = [set(data[col]) for col in data.columns]
        else:
            if len(data) != 3:
                raise ValueError("Must provide exactly 3 sets")
            sets = data
            
        self._setup_figure()
        self._calculate_mixed_colors()
        self._create_venn(sets)
        
        if save:
            if isinstance(save, str):
                plt.savefig(f"{save}.png", dpi=300, bbox_inches="tight")
                plt.savefig(f"{save}.svg", bbox_inches="tight")
            else:
                files = Path.cwd().glob("venn_*.png")
                max_num = max([int(f.stem.split("_")[1]) for f in files], default=-1)
                new_num = max_num + 1
                plt.savefig(f"venn_{new_num:02d}.png", dpi=300, bbox_inches="tight")
                plt.savefig(f"venn_{new_num:02d}.svg", bbox_inches="tight")
                
        return self.fig 