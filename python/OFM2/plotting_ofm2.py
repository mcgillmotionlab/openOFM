import os
import matplotlib.pyplot as plt
import numpy as np

ANGLES = {
    "TibiaGlobalAngles2": ("Tibia vs lab", ("Sagittal", "Coronal", "Traverse")),
    "HindfootGlobalAngles2": ("Hindfoot vs lab", ("Sagittal", "Traverse", "Coronal")),
    "HindfootTibiaAngles2": ("Hindfoot vs tibia", ("Sagittal", "Traverse", "Coronal")),
    "FootTibiaAngles2": ("Whole foot vs tibia", ("Sagittal", "Traverse", "Coronal")),
    "ForefootHindfootAngles2": ("Forefoot vs hindfoot", ("Sagittal", "Traverse", "Coronal")),
    "MedForefootHindfootAngles2": ("Medial forefoot vs hindfoot", ("Sagittal", "Traverse", "Coronal")),
    "LatForefootHindfootAngles2": ("Lateral forefoot vs hindfoot", ("Sagittal", "Traverse", "Coronal")),
    "IntForefootHindfootAngles2": ("Intermediate forefoot vs hindfoot", ("Sagittal", "Traverse", "Coronal")),
    "ForefootTibiaAngles2": ("Forefoot vs tibia", ("Sagittal", "Traverse", "Coronal")),
    "HalluxForefootAngles2": ("Hallux vs forefoot", ("Sagittal", "Coronal", "Traverse")),
    "MedLongArchAngles2": ("Medial longitudinal arch", ("Arch Angle"))
}

FIGURES = {
    "tibia_hindfoot": ("Tibia, hindfoot and foot",
                       ["TibiaGlobalAngles2", "HindfootGlobalAngles2",
                        "HindfootTibiaAngles2", "FootTibiaAngles2"]),
    "forefoot":       ("Forefoot segments",
                       ["ForefootHindfootAngles2", "MedForefootHindfootAngles2",
                        "LatForefootHindfootAngles2", "IntForefootHindfootAngles2",
                        "ForefootTibiaAngles2"]),
    "hallux_arch":    ("Hallux and medial longitudinal arch",
                       ["HalluxForefootAngles2", "MedLongArchAngles2"]),
}


def _available(results, name):
    "check results for available"
    sides = {}
    for side in ("L", "R"):
        arr = results.get(side + name)
        if arr is not None:
            arr = np.asarray(arr, dtype=float)
            if arr.ndim == 2 and np.isfinite(arr).any():
                sides[side] = arr
    return sides


def plot_ofm2_results(results, rate=None, save_dir=None, show=True, dpi=150):
    """Make the OFM2 figures.

    rate     : sample rate in Hz for a time axis in seconds; None plots against frame.
    save_dir : folder for PNG files (created if needed); None does not save.
    show     : call plt.show() at the end.

    Returns {"figures": {name: Figure}, "skipped": [angle names not plotted]}.
    """
    figures, skipped = {}, []

    for fig_name, (fig_title, names) in FIGURES.items():
        rows = []
        for name in names:
            sides = _available(results, name)
            if sides:
                rows.append((name, sides))
            else:
                skipped.append(name)
        if not rows:
            continue

        ncols = max(len(ANGLES[name][1]) for name, _ in rows)
        fig, axes = plt.subplots(len(rows), ncols, squeeze=False, sharex=True,
                                 figsize=(4.2 * ncols, 2.6 * len(rows) + 0.8),
                                 constrained_layout=True)
        fig.suptitle(fig_title, fontsize=13, fontweight="bold")

        for r, (name, sides) in enumerate(rows):
            row_title, comp_labels = ANGLES[name]
            for c in range(ncols):
                ax = axes[r, c]
                if c >= len(comp_labels):
                    ax.set_visible(False)
                    continue
                for side in ("L", "R"):
                    if side in sides:
                        print(f"Plotting {ANGLES[name]} {side}")
                        arr = sides[side]
                        x = np.arange(len(arr)) / rate if rate else np.arange(len(arr))
                        ax.plot(x, arr[:, c], lw=1.4,
                                label="Left" if side == "L" else "Right")
                # keep flat traces from autoscaling into floating-point noise
                lo, hi = ax.get_ylim()
                if hi - lo < 4:
                    mid = (hi + lo) / 2
                    ax.set_ylim(mid - 2, mid + 2)
                ax.axhline(0, color="0.8", lw=0.8, zorder=0)
                ax.grid(alpha=0.25)
                ax.set_title(comp_labels[c], fontsize=10)
                if c == 0:
                    ax.set_ylabel(f"{row_title}\n(deg)", fontsize=9)
                if r == len(rows) - 1:
                    ax.set_xlabel("Time (s)" if rate else "Frame")
            if r == 0:
                axes[0, 0].legend(loc="best", fontsize=8, frameon=False)

        figures[fig_name] = fig
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            fig.savefig(os.path.join(save_dir, f"ofm2_{fig_name}.png"), dpi=dpi)

    if skipped:
        print("Not plotted (not computed): " + ", ".join(sorted(set(skipped))))
    if show:
        plt.show()
    return {"figures": figures, "skipped": sorted(set(skipped))}