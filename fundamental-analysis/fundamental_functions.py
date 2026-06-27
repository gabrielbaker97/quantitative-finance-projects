import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
colorcodes = {
    "primary":  "dodgerblue",
    "secondary":"#2e75b6",
    "accent":   "magenta",
    "red":      "#c00000",
    "grey":     "#808080",
    "pos":      "forestgreen",
    "neg":      "firebrick",
}
def cagr(series, start_yr, end_yr):
    n = end_yr - start_yr
    return ((series[end_yr] / series[start_yr]) ** (1/n) - 1) * 100

def bar_chart(pl, title, metric, yname, conditional_colors=False):
    colors = ([colorcodes["pos"] if v >= 0 else colorcodes["neg"] for v in pl[metric]]
              if conditional_colors else colorcodes["primary"])

    fig, ax = plt.subplots(figsize=(14, 5))
    values = pl[metric] if yname == '%' else pl[metric] / 1000
    ax.bar(pl.index, values, color=colors, alpha=0.85, zorder=2)

    if conditional_colors:
        ax.axhline(0, color='black', linewidth=0.8, zorder=3)

    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylabel(yname)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}'))
    ax.grid(axis='y', alpha=0.4)
    plt.xticks(pl.index)
    plt.tight_layout()
    plt.show()

def line_chart(df, pl, title, yname, bar_col='Revenue', line_cols=('EBIT', 'Net profit')):
    line_colors = [colorcodes["primary"], colorcodes["secondary"], colorcodes["accent"]]
    markers = ['o', 's', '^']

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # Left: line trends
    ax = axes[0]
    for col in df.columns:
        ax.plot(df.index, df[col], marker='o', ms=4, label=col)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylabel(yname)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}'))
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.4)
    plt.sca(ax)
    plt.xticks(df.index)

    # Right: bar + dual-axis lines
    ax = axes[1]
    ax2 = ax.twinx()
    ax.bar(pl.index, pl[bar_col] / 1000, color=colorcodes["secondary"], alpha=0.35, label=f'{bar_col} (LHS)')
    for i, col in enumerate(line_cols):
        ax2.plot(pl.index, pl[col] / 1000, color=line_colors[i], marker=markers[i], ms=4, label=f'{col} (RHS)')
    ax.set_title(f'{bar_col} vs {" & ".join(line_cols)} (DKKbn)', fontsize=13, fontweight='bold')
    ax.set_ylabel(f'{bar_col} (DKKbn)', color=colorcodes["grey"])
    ax2.set_ylabel(f'{" / ".join(line_cols)} (DKKbn)', color=colorcodes["primary"])
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()