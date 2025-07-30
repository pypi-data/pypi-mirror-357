# Created by Cees Dekker Lab at the Delft University of Technology
# Refactored by Thijn Hoekstra
from importlib import resources as impresources

from varv import config
from varv.classification import assets, predictdna

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

inp_file = impresources.files(assets) / "DNA_6mer_prediction_model_cv.csv"

DNA_MODEL = pd.read_csv(inp_file)


def predict(sequence, model: pd.DataFrame = None, k_mer_size=6, nan_policy="omit"):
    """Predict constant voltage signal.

    Assumes two steps at each k_mer in the sequence, as Hel308 takes nuleotide
    half-steps. Returns a signal from 3-prime end to 5-prime end.

    Args:
        sequence (str): Sequence in 5-prime to 3-prime format.
        model: Dataframe of DNA model
        k_mer_size: k-mer size. Defaults to 6.
        nan_policy: Whether to return NaN for the steps in the sequence that do not have a k-mer (at the beginning and
            end of the sequence) Defaults to "omit", in which case these steps are not included..
    """
    if model is None:
        model = DNA_MODEL

    sequence = sequence[::-1]  # Reverse the string (3'->5')
    constriction_kmer_offset = -4

    sub_6mer = list(predictdna.sliding_window(sequence, k_mer_size))
    DNA_prediction_mean = np.zeros(len(sub_6mer) * 2)
    DNA_prediction_std = np.zeros(len(sub_6mer) * 2)

    for j, kmer in enumerate(sub_6mer):
        kmer_index = model.index[model["kmer_pull_3_5"] == kmer].tolist()
        if kmer_index:
            kmer_index = kmer_index[0]
            DNA_prediction_mean[j * 2] = model.loc[kmer_index, "pre_mean"]
            DNA_prediction_mean[j * 2 + 1] = model.loc[kmer_index, "post_mean"]
            DNA_prediction_std[j * 2] = model.loc[kmer_index, "pre_std"]
            DNA_prediction_std[j * 2 + 1] = model.loc[kmer_index, "post_std"]

    # Organize results into DataFrame
    result_length = 2 * len(sequence)
    mean = np.full(result_length, np.nan)
    std = np.full(result_length, np.nan)
    base = [""] * result_length
    mode = [""] * result_length
    step = np.arange(0, result_length) + constriction_kmer_offset

    start_index = -constriction_kmer_offset
    end_index = len(DNA_prediction_mean) - constriction_kmer_offset
    mean[start_index:end_index] = DNA_prediction_mean
    std[start_index:end_index] = DNA_prediction_std

    for j in range(len(sequence)):
        base[2 * j] = sequence[j]
        base[2 * j + 1] = sequence[j]
        mode[2 * j] = "pre"
        mode[2 * j + 1] = "post"

    table_result = pd.DataFrame(
        {"step": step, "base": base, "mode": mode, "mean": mean, "std": std}
    )

    if nan_policy == "omit":
        table_result = table_result[~table_result["mean"].isna()]
        table_result.reset_index(drop=True, inplace=True)

    # if store_kmers:
    #     # Each pair of results in table has same k-mer due to helicase half-steps
    #     table_result["kmer"] = list(itertools.chain.from_iterable (zip(sub_6mer, sub_6mer)))

    return table_result


def visualize_template_dna(DNA_prediction_results):
    nan_filter = DNA_prediction_results["mean"].notna()

    # Create plot
    fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE)
    ax.grid(True)

    # Plot assets
    ax.step(
        DNA_prediction_results[nan_filter]["step"],
        DNA_prediction_results[nan_filter]["mean"],
        where="mid",
        linewidth=1.3,
    )
    ax.errorbar(
        DNA_prediction_results[nan_filter]["step"],
        DNA_prediction_results[nan_filter]["mean"],
        yerr=DNA_prediction_results[nan_filter]["std"],
        fmt="none",
        elinewidth=1,
    )

    # Add base labels
    base_y_coor = 0.13
    for i in range(0, len(DNA_prediction_results), 2):
        base_char = DNA_prediction_results["base"].iloc[i]
        base_coor = DNA_prediction_results["step"].iloc[i] + 0.5
        ax.text(base_coor, base_y_coor, base_char, fontsize=12)

    # Set axis limits and labels
    ax.set_ylim(0.1, 0.5)
    ax.set_xlim(-4, len(DNA_prediction_results) - 2)
    ax.set_xlabel("Step number", fontsize=15)
    ax.set_ylabel("Relative levels", fontsize=15)
    ax.tick_params(axis="both", which="major", labelsize=12)

    # Show plot
    # plt.show()
    # plt.savefig(f'{plots_path}template_DNA_prediction.svg')
    # plt.savefig(f'{plots_path}template_DNA_prediction.png', dpi=300)
    return None
