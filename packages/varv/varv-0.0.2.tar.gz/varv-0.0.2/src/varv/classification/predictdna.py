#
#      Copyright (C) 2024 Thijn Hoekstra
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from collections import deque
from importlib import resources as impresources
from itertools import islice

import numpy as np
import pandas as pd

from varv import config
from varv.classification import assets

inp_file = impresources.files(assets) / "DNA_6mer_prediction_model.csv"

DNA_MODEL = pd.read_csv(inp_file, index_col=0)


def sliding_window(s: str, n: int):
    """Collect data into overlapping fixed-length chunks or blocks.

    From itertools recipes
    """
    iterator = iter(s)
    window = deque(islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield "".join(window)


def predict(sequence, model: pd.DataFrame = None, k_mer_size=6, reduced=True):
    """Predict from 3' to 5' of sequence.

    Assumes two steps at each k_mer in the sequence, as Hel308 takes nuleotide
    half-steps. Parameter sequence should be from 5-prime to 3-prime
    """
    if model is None:
        model = DNA_MODEL

    sequence = sequence[::-1]  # Reverse the sequence (3'->5')

    sizes = np.unique([len(idx) for idx in model.index])
    if len(sizes) != 1:
        raise ValueError(f"DNA model contains kmers of various sizes: {sizes}")
    elif sizes[0] != k_mer_size:
        raise ValueError(
            f"Expected model to have kmers of size {k_mer_size} but " f"got {sizes[0]}"
        )

    # Two hel308 steps per nucleotide
    n_steps = get_n_steps(len(sequence), k_mer_size)

    if reduced:
        coef_cols = model.filter(like=config.COEF_FORMAT.replace("{}", "")).columns
        cov_cols = model.filter(like=config.COV_FORMAT.replace("{},{}", "")).columns
        index = np.arange(n_steps)
        columns = coef_cols.to_list() + cov_cols.to_list()
    else:
        index = pd.MultiIndex.from_product(
        [np.arange(n_steps), [0]], names=["step", "period"]
        )
        columns = model.filter(like="g_").columns


    predicted_df = pd.DataFrame(
        index=index, columns=columns, dtype=np.float64
    )

    for j, k_mer in enumerate(sliding_window(sequence.upper(), k_mer_size)):
        predicted_df.iloc[j * 2 : j * 2 + 2, :] = model.loc[k_mer, columns].to_numpy()

    return predicted_df


def get_n_steps(l, k_mer_size):
    return (l - k_mer_size + 1) * 2
