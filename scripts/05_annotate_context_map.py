"""
Create an annotated version of Figure 1 while preserving the original map.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.offsetbox import AnnotationBbox, OffsetImage


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "figure_sources"
REV_DIR = ROOT / "output"


def add_label(ax: plt.Axes) -> None:
    ax.text(
        0.025,
        0.955,
        "RMSP helicopter-route context",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        color="#111111",
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "white",
            "edgecolor": "#4d4d4d",
            "alpha": 0.88,
            "linewidth": 0.8,
        },
    )


def add_legend(ax: plt.Axes, aerodrome_marker) -> None:
    x0, y0 = 0.64, 0.045
    width, height = 0.335, 0.255
    box = patches.FancyBboxPatch(
        (x0, y0),
        width,
        height,
        transform=ax.transAxes,
        boxstyle="round,pad=0.018",
        facecolor="white",
        edgecolor="#4d4d4d",
        linewidth=0.8,
        alpha=0.88,
        zorder=5,
    )
    ax.add_patch(box)

    rows = [
        ("point", "#ffd83d", "helipads"),
        ("line", "#24136f", "mandatory REH routes"),
        ("line", "#f2a1b2", "recommended REH routes"),
        ("poly", "#f4a62a", "CTR areas"),
        ("pin_image", "#d9341f", "airport/aerodrome markers"),
    ]

    for i, (kind, color, text) in enumerate(rows):
        y = y0 + height - 0.042 - i * 0.042
        if kind == "point":
            ax.scatter(
                [x0 + 0.045],
                [y],
                transform=ax.transAxes,
                s=34,
                facecolor=color,
                edgecolor="#805f00",
                linewidth=0.6,
                zorder=6,
            )
        elif kind == "line":
            ax.plot(
                [x0 + 0.022, x0 + 0.067],
                [y, y],
                transform=ax.transAxes,
                color=color,
                linewidth=2.6,
                solid_capstyle="round",
                zorder=6,
            )
        elif kind == "poly":
            rect = patches.Rectangle(
                (x0 + 0.024, y - 0.018),
                0.041,
                0.031,
                transform=ax.transAxes,
                facecolor="#f4a62a",
                edgecolor="#c98214",
                linewidth=1.0,
                alpha=0.35,
                zorder=6,
            )
            ax.add_patch(rect)
        else:
            imagebox = OffsetImage(aerodrome_marker, zoom=0.52)
            ab = AnnotationBbox(
                imagebox,
                (x0 + 0.045, y),
                xycoords=ax.transAxes,
                frameon=False,
                zorder=6,
            )
            ax.add_artist(ab)

        ax.text(
            x0 + 0.085,
            y,
            text,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=8.4,
            color="#111111",
            zorder=6,
        )


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    image = plt.imread(SOURCE_DIR / "ctr.png")
    aerodrome_marker = plt.imread(SOURCE_DIR / "aerodrome_red_marker.png")
    height, width = image.shape[:2]
    fig_width = 7.6
    fig_height = fig_width * height / width

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.imshow(image)
    ax.set_axis_off()
    add_label(ax)
    add_legend(ax, aerodrome_marker)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    REV_DIR.mkdir(exist_ok=True)
    fig.savefig(REV_DIR / "ctr_annotated.pdf", bbox_inches="tight", pad_inches=0.01)
    fig.savefig(REV_DIR / "ctr_annotated.png", dpi=300, bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)
    print("Saved ctr_annotated.pdf and ctr_annotated.png")


if __name__ == "__main__":
    main()
