"""
Create publication-ready annotated versions of the original BlueSky screenshots.

The output preserves the simulator snapshots and adds a compact scenario label
and legend so the figures remain authentic BlueSky outputs while being easier
to read in the manuscript.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "figure_sources"
REV_DIR = ROOT / "output"

SNAPSHOTS = {
    "No conflict resolution": {
        "input": SOURCE_DIR / "bluesky_bimtra_mvp_off.jpg",
        "pdf": REV_DIR / "bluesky_bimtra_mvp_off_annotated.pdf",
        "png": REV_DIR / "bluesky_bimtra_mvp_off_annotated.png",
    },
    "MVP 60 s lookahead": {
        "input": SOURCE_DIR / "bluesky_bimtra_mvp_60.jpg",
        "pdf": REV_DIR / "bluesky_bimtra_mvp_60_annotated.pdf",
        "png": REV_DIR / "bluesky_bimtra_mvp_60_annotated.png",
    },
    "MVP 120 s lookahead": {
        "input": SOURCE_DIR / "bluesky_bimtra_mvp_120.jpg",
        "pdf": REV_DIR / "bluesky_bimtra_mvp_120_annotated.pdf",
        "png": REV_DIR / "bluesky_bimtra_mvp_120_annotated.png",
    },
}


def add_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        0.025,
        0.94,
        label,
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


def add_legend(ax: plt.Axes) -> None:
    x0, y0 = 0.67, 0.055
    width, height = 0.305, 0.215
    box = patches.FancyBboxPatch(
        (x0, y0),
        width,
        height,
        transform=ax.transAxes,
        boxstyle="round,pad=0.018",
        facecolor="white",
        edgecolor="#4d4d4d",
        linewidth=0.8,
        alpha=0.86,
        zorder=5,
    )
    ax.add_patch(box)

    rows = [
        ("#00d8d8", "simulated trajectories"),
        ("#40f060", "aircraft vectors/labels"),
        ("#d9d9d9", "aerodrome markers"),
    ]
    for i, (color, text) in enumerate(rows):
        y = y0 + height - 0.055 - i * 0.06
        ax.plot(
            [x0 + 0.025, x0 + 0.08],
            [y, y],
            transform=ax.transAxes,
            color=color,
            linewidth=2.2,
            solid_capstyle="round",
            zorder=6,
        )
        ax.text(
            x0 + 0.095,
            y,
            text,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=9.5,
            color="#111111",
            zorder=6,
        )


def annotate(label: str, paths: dict[str, Path]) -> None:
    image = plt.imread(paths["input"])
    height, width = image.shape[:2]
    fig_width = 7.6
    fig_height = fig_width * height / width

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.imshow(image)
    ax.set_axis_off()
    add_label(ax, label)
    add_legend(ax)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    fig.savefig(paths["pdf"], bbox_inches="tight", pad_inches=0.01)
    fig.savefig(paths["png"], dpi=300, bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)
    print(f"Saved {paths['pdf'].name} and {paths['png'].name}")


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    REV_DIR.mkdir(exist_ok=True)
    for label, paths in SNAPSHOTS.items():
        annotate(label, paths)


if __name__ == "__main__":
    main()
