#!/usr/bin/env python

import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Union, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import typer

from atg.utils import BackgroundColor, OutputFormat

app = typer.Typer()

@dataclass
class PlotConfig:
    """Configuration for LEfSe plot."""
    feature_font_size: int = 7
    output_format: OutputFormat = OutputFormat.PNG
    dpi: int = 300
    title: str = ""
    title_font_size: int = 12
    class_legend_font_size: int = 10
    width: int = 7
    left_space: float = 0.2
    right_space: float = 0.1
    autoscale: bool = True
    back_color: BackgroundColor = BackgroundColor.WHITE
    n_scl: bool = False
    max_feature_len: int = 60
    all_feats: str = ""
    otu_only: bool = False
    report_features: bool = False


class LefsePlotter:
    """Class for creating LEfSe plots."""
    
    # Color palette
    COLORS = [
        "#E64B35B2",
        "#00A087B2",
        "#4DBBD5B2",
        "#3C5488B2",
        "#F39B7FB2",
        "#8491B4B2",
        "#91D1C2B2",
        "#DC0000B2",
    ]
    
    def __init__(self, config: PlotConfig) -> None:
        """Initialize the plotter with configuration.
        
        Args:
            config: Plot configuration parameters
        """
        self.config = config
        assert isinstance(config, PlotConfig), "Config must be a PlotConfig instance"
    
    def read_data(self, input_file: str, output_file: str) -> pd.DataFrame:
        """Read and process input data.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            
        Returns:
            DataFrame containing processed data
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If no differentially abundant features found
        """
        assert os.path.exists(input_file), f"Input file {input_file} does not exist"
        
        try:
            with open(input_file, "r", encoding="utf-8") as inp:
                if not self.config.otu_only:
                    rows = [line.strip().split()[:-1] for line in inp.readlines() 
                           if len(line.strip().split()) > 3]
                else:
                    rows = [line.strip().split()[:-1] for line in inp.readlines() 
                           if len(line.strip().split()) > 3 and 
                           len(line.strip().split()[0].split(".")) == 8]
        except Exception as e:
            raise FileNotFoundError(f"Error reading input file: {str(e)}")
        
        classes = list({v[2] for v in rows if len(v) > 2})
        if len(classes) < 1:
            print(f"No differentially abundant features found in {input_file}")
            os.system("touch " + output_file)
            sys.exit(1)
        
        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=['feature', 'subclass', 'class', 'score'])
        df['score'] = df['score'].astype(float)
        return df
    
    def create_plot(self, df: pd.DataFrame, output_file: str) -> None:
        """Create and save the LEfSe plot.
        
        Args:
            df: DataFrame containing plot data
            output_file: Path to save the plot
            
        Raises:
            ValueError: If DataFrame is empty or missing required columns
        """
        assert not df.empty, "DataFrame cannot be empty"
        assert all(col in df.columns for col in ['feature', 'class', 'score']), \
            "DataFrame must contain 'feature', 'class', and 'score' columns"
        
        # Calculate dimensions
        head = 0.75
        tail = 0.5
        ht = head + tail
        ints = max(len(df) * 0.2, 1.5)
        
        # Set up the figure
        fig = plt.figure(
            figsize=(self.config.width, ints + ht),
            edgecolor=self.config.back_color.value,
            facecolor=self.config.back_color.value,
        )
        
        # Create subplot
        ax = fig.add_subplot(111, frame_on=False, facecolor=self.config.back_color.value)
        ls, rs = self.config.left_space, 1.0 - self.config.right_space
        
        plt.subplots_adjust(
            left=ls,
            right=rs,
            top=1 - head * (1.0 - ints / (ints + ht)),
            bottom=tail * (1.0 - ints / (ints + ht)),
        )
        
        # Set foreground color based on background
        fore_color = "k" if self.config.back_color == BackgroundColor.WHITE else "w"
        
        # Create positions for bars
        pos = np.arange(len(df))
        
        # Sort data if needed
        if len(df['class'].unique()) == 2:
            df = df.sort_values('score', key=lambda x: abs(x) * (df['class'].map({df['class'].unique()[0]: 1, df['class'].unique()[1]: -1})))
        else:
            mmax = df['score'].abs().max()
            df = df.sort_values('score', key=lambda x: abs(x) / mmax + (df['class'].map({c: i+1 for i, c in enumerate(df['class'].unique())})))
        
        # Plot bars
        added = []
        for i, (_, row) in enumerate(df.iterrows()):
            indcl = list(df['class'].unique()).index(row['class'])
            lab = str(row['class']) if row['class'] not in added else None
            added.append(row['class'])
            
            col = self.COLORS[indcl % len(self.COLORS)]
            if self.config.all_feats:
                col = self.COLORS[list(self.config.all_feats.split(":")).index(row['class']) % len(self.COLORS)]
            
            vv = abs(float(row['score']))
            if len(df['class'].unique()) == 2:
                vv *= (1 if indcl == 0 else -1)
            
            ax.barh(
                pos[i],
                vv,
                align="center",
                color=col,
                label=lab,
                height=0.8,
                edgecolor=fore_color,
            )
        
        # Add feature labels
        mv = df['score'].abs().max()
        for i, (_, row) in enumerate(df.iterrows()):
            indcl = list(df['class'].unique()).index(row['class'])
            rr = row['feature'] if self.config.n_scl < 0 else ".".join(row['feature'].split(".")[-self.config.n_scl:])
            
            if len(df['class'].unique()) == 2 and indcl == 1:
                ax.text(
                    mv / 40.0,
                    float(i),
                    rr,
                    horizontalalignment="left",
                    verticalalignment="center",
                    size=self.config.feature_font_size,
                    color=fore_color,
                )
            else:
                ax.text(
                    -mv / 40.0,
                    float(i),
                    rr,
                    horizontalalignment="right",
                    verticalalignment="center",
                    size=self.config.feature_font_size,
                    color=fore_color,
                )
        
        self._customize_plot(ax, fore_color, ints, ht, mv)
        self._save_plot(output_file, fore_color)
    
    def _customize_plot(self, ax: plt.Axes, fore_color: str, ints: float, ht: float, mv: float) -> None:
        """Customize plot appearance.
        
        Args:
            ax: Matplotlib axes object
            fore_color: Color for foreground elements
            ints: Internal spacing
            ht: Height spacing
            mv: Maximum value for scaling
        """
        ax.set_title(
            self.config.title,
            size=self.config.title_font_size,
            y=1.0 + 0.8 * (1.0 - ints / (ints + ht)),
            color=fore_color,
        )
        ax.set_xlabel("LDA SCORE (log 10)", color=fore_color)
        ax.set_ylabel("")
        
        # Remove y-axis ticks
        ax.set_yticks([])
        
        # Set grid
        ax.set_axisbelow(True)
        ax.xaxis.grid(linestyle="--", linewidth=0.8, dashes=(2, 3), color=fore_color, alpha=0.5)
        
        # Set x-axis limits
        xlim = ax.get_xlim()
        if self.config.autoscale:
            round_1 = round((abs(xlim[0]) + abs(xlim[1])) / 10, 4)
            round_2 = round(round_1 * 100, 0)
            ran = np.arange(0.0001, round_2 / 100)
            if 1 < len(ran) < 100:
                min_ax = min(xlim[1] + 0.0001, round_2 / 100)
                ax.set_xticks(np.arange(xlim[0], xlim[1] + 0.0001, min_ax))
        
        # Set y-axis limits
        ax.set_ylim((-0.5, len(ax.patches) - 0.5))
        
        # Add legend
        leg = ax.legend(
            bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
            loc=3,
            ncol=5,
            borderaxespad=0.0,
            frameon=False,
            prop={"size": self.config.class_legend_font_size},
        )
        
        # Set legend text color
        for o in leg.findobj(lambda x: hasattr(x, 'set_color') and not hasattr(x, 'set_facecolor')):
            o.set_color(fore_color)
        for o in ax.findobj(lambda x: hasattr(x, 'set_color') and not hasattr(x, 'set_facecolor')):
            o.set_color(fore_color)
    
    def _save_plot(self, output_file: str, fore_color: str) -> None:
        """Save the plot to file.
        
        Args:
            output_file: Path to save the plot
            fore_color: Color for foreground elements
            
        Raises:
            IOError: If plot cannot be saved
        """
        try:
            plt.savefig(
                output_file,
                format=self.config.output_format,
                facecolor=self.config.back_color.value,
                edgecolor=fore_color,
                dpi=self.config.dpi,
                bbox_inches='tight',
                pad_inches=0.1,
            )
        except Exception as e:
            raise IOError(f"Error saving plot: {str(e)}")
        finally:
            plt.close()


@app.command()
def plot_results(
    input_file: str = typer.Option(..., "--input", "-i", show_default=False, help="tab delimited input file"),
    output_file: str = typer.Option(..., "--output", "-o", show_default=False, help="the file for the output image"),
    feature_font_size: int = typer.Option(7, "--feature-font-size", "-z", show_default=True, help="the font size for the features"),
    output_format: OutputFormat = typer.Option(OutputFormat.PNG, "--format", "-f", show_default=True, help="the format for the output image (png, svg, pdf)"),
    dpi: int = typer.Option(300, "--dpi", "-d", show_default=True, help="the dpi for the output image"),
    title: str = typer.Option("", "--title", "-t", show_default=False, help="the title for the plot"),
    title_font_size: int = typer.Option(12, "--title-font-size", "-Z", show_default=True, help="the font size for the title"),
    class_legend_font_size: int = typer.Option(10, "--class-legend-font-size", "-c", show_default=True, help="the font size for the class legend"),
    width: int = typer.Option(7, "--width", "-w", show_default=True, help="the width of the plot"),
    left_space: float = typer.Option(0.2, "--left-space", "-l", show_default=True, help="the left space of the plot"),
    right_space: float = typer.Option(0.1, "--right-space", "-r", show_default=True, help="the right space of the plot"),
    autoscale: bool = typer.Option(True, "--autoscale", "-a", show_default=True, help="autoscale the plot"),
    back_color: BackgroundColor = typer.Option(BackgroundColor.WHITE, "--background-color", "-b", show_default=True, help="the background color (w for white, k for black)"),
    n_scl: bool = typer.Option(False, "--subclades", "-s", show_default=True, help="number of label levels to be displayed"),
    max_feature_len: int = typer.Option(60, "--max-feature-len", "-m", show_default=True, help="the maximum length of the feature name"),
    all_feats: str = typer.Option("", "--all-feats", "-A", show_default=False, help="show all features"),
    otu_only: bool = typer.Option(False, "--otu-only", "-O", show_default=True, help="Plot only species resolved OTUs"),
    report_features: bool = typer.Option(False, "--report-features", "-R", show_default=False, help="report features to STDOUT"),
) -> None:
    """Main function to create LEfSe plot."""
    # Create configuration
    config = PlotConfig(
        feature_font_size=feature_font_size,
        output_format=output_format,
        dpi=dpi,
        title=title,
        title_font_size=title_font_size,
        class_legend_font_size=class_legend_font_size,
        width=width,
        left_space=left_space,
        right_space=right_space,
        autoscale=autoscale,
        back_color=back_color,
        n_scl=n_scl,
        max_feature_len=max_feature_len,
        all_feats=all_feats,
        otu_only=otu_only,
        report_features=report_features,
    )
    
    # Create plotter and generate plot
    plotter = LefsePlotter(config)
    df = plotter.read_data(input_file, output_file)
    plotter.create_plot(df, output_file)
