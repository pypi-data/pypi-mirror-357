"""Volcano plot implementation using matplotlib/seaborn.

This module provides functionality to create volcano plots, which are used to visualize
differential expression results. The implementation uses matplotlib and seaborn for
plotting.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path

import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from adjustText import adjust_text


@dataclass
class VolcanoConfig:
    """Configuration for volcano plot."""
    log2fc: str = "log2FoldChange"
    pvalue: str = "padj"
    symbol: str = "symbol"
    base_mean: Optional[str] = None
    pval_thresh: float = 0.05
    log2fc_thresh: float = 0.75
    to_label: Union[int, List[str]] = 5
    color_dict: Optional[Dict[str, List[str]]] = None
    shape_dict: Optional[Dict[str, List[str]]] = None
    fontsize: int = 10
    colors: List[str] = None
    top_right_frame: bool = False
    figsize: Tuple[int, int] = (5, 5)
    legend_pos: Tuple[float, float] = (1.4, 1)
    point_sizes: Tuple[int, int] = (15, 150)
    shapes: Optional[List[str]] = None
    shape_order: Optional[List[str]] = None
    
    def __post_init__(self):
        """Set default colors if not provided."""
        if self.colors is None:
            self.colors = ["dimgrey", "lightgrey", "black"]


class VolcanoPlotter:
    """Class for creating volcano plots using matplotlib/seaborn."""
    
    def __init__(self, config: Optional[VolcanoConfig] = None):
        """Initialize the plotter with configuration.
        
        Args:
            config: Plot configuration parameters. If None, uses default values.
        """
        self.config = config or VolcanoConfig()
        self.fig = None
        self.ax = None
        
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for plotting.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Processed DataFrame
            
        Raises:
            ValueError: If required columns are missing
        """
        required_cols = [self.config.log2fc, self.config.pvalue, self.config.symbol]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        df = df.dropna()
        if df[self.config.pvalue].min() == 0:
            print("0s encountered for p value, imputing 1e-323")
            print("impute your own value if you want to avoid this")
            df[self.config.pvalue][df[self.config.pvalue] == 0] = 1e-323
            
        df["nlog10"] = -np.log10(df[self.config.pvalue])
        df["sorter"] = df["nlog10"] * df[self.config.log2fc]
        
        if self.config.base_mean is not None:
            df["logBaseMean"] = np.log(df[self.config.base_mean])
            self.config.base_mean = "logBaseMean"
            
        return df
        
    def _prepare_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare labels for plotting.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            DataFrame with labels
        """
        if isinstance(self.config.to_label, int):
            label_df = pd.concat((
                df.sort_values("sorter")[-self.config.to_label:],
                df.sort_values("sorter")[0:self.config.to_label]
            ))
        else:
            label_df = df[df[self.config.symbol].isin(self.config.to_label)]
            
        return label_df
        
    def _map_colors(self, df: pd.DataFrame, label_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Map colors to data points.
        
        Args:
            df: Processed DataFrame
            label_df: DataFrame with labels
            
        Returns:
            Tuple of (DataFrame with colors, list of color categories)
        """
        def map_color_simple(row):
            log2fc, symbol, nlog10 = row
            if symbol in label_df[self.config.symbol].tolist():
                return "picked"
            if abs(log2fc) < self.config.log2fc_thresh or nlog10 < -np.log10(self.config.pval_thresh):
                return "not DE"
            return "DE"
            
        def map_color_complex(row):
            log2fc, symbol, nlog10 = row
            for k in self.config.color_dict:
                if symbol in self.config.color_dict[k]:
                    return k
            if abs(log2fc) < self.config.log2fc_thresh or nlog10 < -np.log10(self.config.pval_thresh):
                return "not DE"
            return "DE"
            
        if self.config.color_dict is None:
            df["color"] = df[[self.config.log2fc, self.config.symbol, "nlog10"]].apply(
                map_color_simple, axis=1
            )
            hues = ["DE", "not DE", "picked"][:len(df.color.unique())]
        else:
            df["color"] = df[[self.config.log2fc, self.config.symbol, "nlog10"]].apply(
                map_color_complex, axis=1
            )
            user_added_cats = [x for x in df.color.unique() if x not in ["DE", "not DE"]]
            hues = ["DE", "not DE"] + user_added_cats
            hues = hues[:len(df.color.unique())]
            
            if self.config.colors == ["dimgrey", "lightgrey", "black"]:
                self.config.colors = [
                    "dimgrey", "lightgrey", "tab:blue", "tab:orange", "tab:green",
                    "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:olive", "tab:cyan"
                ]
                
        return df, hues
        
    def _map_shapes(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str], Optional[List[str]]]:
        """Map shapes to data points.
        
        Args:
            df: Processed DataFrame
            
        Returns:
            Tuple of (DataFrame with shapes, shape column name, shape order)
        """
        if self.config.shape_dict is None:
            return df, None, None
            
        def map_shape(symbol):
            for k in self.config.shape_dict:
                if symbol in self.config.shape_dict[k]:
                    return k
            return "other"
            
        df["shape"] = df[self.config.symbol].map(map_shape)
        user_added_cats = [x for x in df["shape"].unique() if x != "other"]
        shape_order = ["other"] + user_added_cats
        
        if self.config.shapes is None:
            shapes = ["o", "^", "s", "X", "*", "d"]
        else:
            shapes = self.config.shapes
            
        shapes = shapes[:len(df["shape"].unique())]
        
        return df, "shape", shape_order
        
    def _create_plot(self, df: pd.DataFrame, label_df: pd.DataFrame, hues: List[str],
                    shape_col: Optional[str], shape_order: Optional[List[str]]) -> None:
        """Create the volcano plot.
        
        Args:
            df: Processed DataFrame
            label_df: DataFrame with labels
            hues: List of color categories
            shape_col: Optional shape column name
            shape_order: Optional shape order
        """
        self.fig = plt.figure(figsize=self.config.figsize)
        self.ax = sns.scatterplot(
            data=df,
            x=self.config.log2fc,
            y="nlog10",
            hue="color",
            hue_order=hues,
            palette=self.config.colors[:len(df.color.unique())],
            size=self.config.base_mean,
            sizes=self.config.point_sizes,
            style=shape_col,
            style_order=shape_order,
            markers=self.config.shapes
        )
        
        texts = []
        for _, row in label_df.iterrows():
            txt = plt.text(
                x=row[self.config.log2fc],
                y=row["nlog10"],
                s=row[self.config.symbol],
                fontsize=self.config.fontsize,
                weight="bold"
            )
            txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground="w")])
            texts.append(txt)
            
        adjust_text(texts, arrowprops=dict(arrowstyle="-", color="k", zorder=5))
        
        pval_thresh = -np.log10(self.config.pval_thresh)
        self.ax.axhline(pval_thresh, zorder=0, c="k", lw=2, ls="--")
        self.ax.axvline(self.config.log2fc_thresh, zorder=0, c="k", lw=2, ls="--")
        self.ax.axvline(-self.config.log2fc_thresh, zorder=0, c="k", lw=2, ls="--")
        
        for axis in ["bottom", "left", "top", "right"]:
            self.ax.spines[axis].set_linewidth(2)
            
        if not self.config.top_right_frame:
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            
        self.ax.tick_params(width=2)
        plt.xticks(size=11, weight="bold")
        plt.yticks(size=11, weight="bold")
        plt.xlabel("$log_{2}$ fold change", size=15)
        plt.ylabel("-$log_{10}$ FDR", size=15)
        
        plt.legend(
            loc=1,
            bbox_to_anchor=self.config.legend_pos,
            frameon=False,
            prop={"weight": "bold"}
        )
        
    def plot(self, data: Union[str, Path, pd.DataFrame], save: Union[bool, str] = False) -> plt.Figure:
        """Create volcano plot from data.
        
        Args:
            data: DataFrame or path to CSV file
            save: Whether to save the plot. If string, save to that path.
            
        Returns:
            matplotlib Figure object
            
        Raises:
            ValueError: If data is invalid
            FileNotFoundError: If input file doesn't exist
        """
        if isinstance(data, (str, Path)):
            df = pd.read_csv(data)
        else:
            df = data.copy(deep=True)
            
        df = self._prepare_data(df)
        label_df = self._prepare_labels(df)
        df, hues = self._map_colors(df, label_df)
        df, shape_col, shape_order = self._map_shapes(df)
        
        self._create_plot(df, label_df, hues, shape_col, shape_order)
        
        if save:
            if isinstance(save, str):
                plt.savefig(f"{save}.png", dpi=300, bbox_inches="tight")
                plt.savefig(f"{save}.svg", bbox_inches="tight")
            else:
                files = Path.cwd().glob("volcano_*.png")
                max_num = max([int(f.stem.split("_")[1]) for f in files], default=-1)
                new_num = max_num + 1
                plt.savefig(f"volcano_{new_num:02d}.png", dpi=300, bbox_inches="tight")
                plt.savefig(f"volcano_{new_num:02d}.svg", bbox_inches="tight")
                
        return self.fig 