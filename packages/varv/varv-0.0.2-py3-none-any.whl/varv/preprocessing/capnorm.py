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
import json
from importlib import resources as impresources

import numpy as np
import pandas as pd
import scipy
import sklearn
from numpy.polynomial import Polynomial

from varv.feature_extraction import assets
from varv.preprocessing import capcomp

inp_file_calibration = impresources.files(assets) / "calibration_metrics.json"

with open(inp_file_calibration) as f:
    DEFAULT_CALIBRATION = json.load(f)


def normalize(g_df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes a conductance DataFrame.

    Calculates the mean conductance curve for each step. This mean conductance curve represents the
    position-independent component of the conductance, i.e. the conductance-voltage relationship that
    is independent of the position of the DNA/peptide in the pore. This component arises because of
    the non-Ohmic nature of the conductance of the ionic current around a charged molecule in the
    pore constriction. This component is then subtracted from the conductance curve at each set to
    yield the position-independent component of the conductance curve.
    """
    return g_df - get_mean_curves(g_df).mean(axis=0)


def fraying_correction(g_df: pd.DataFrame, v_ref: np.ndarray = None) -> pd.DataFrame:
    """Applies fraying correction

    At high voltages, the polymer in the constriction is stretched out, causing a lower nuber of
    mononomers (nucleotides for DNA) to contribute to the ionic current. This leads to an
    exaggerated high ionic current at high voltages.

    Fraying correction compensates for this phenomenon. At each step, two properties are calculated:
    (1) the mean conductance at that step and (2) the slope `m` of the conductance curve at that step.
    These two values together represent the position-independent relation between the mean conductance
    of a step, and the slope of the conductance curve at that step. A regression is done to find
    this relation and subtract the mean-conductance dependent slope from each conductance curve.

    This method does not work well for intermediate processing steps and on short reads, so is only
    recommended for final processing of long reads.


    """

    if v_ref is None:
        v_ref = capcomp.SPACING_DNA["v"]

    g_means = get_means(g_df)
    m = get_ms(g_df, v_ref)

    alpha = get_alpha(g_means, m)

    corrector = alpha * g_df * v_ref

    return g_df - corrector


def get_alpha(g_means: np.ndarray, m: np.ndarray) -> float:
    """Calculate the relation between the average conductance all steps and the slopes of
    the current conductance curve at each step.

    Yields the slope of this relation, i.e. the coefficient used to calculate the position-independent
    slope at a step from the mean conductance of that step.

    Uses the robust RANSAC method for regression.

    """

    ransac = sklearn.linear_model.RANSACRegressor(random_state=0, max_trials=1000)
    ransac.fit(g_means.reshape(-1, 1), m)

    return ransac.estimator_.coef_[0]


def get_means(g_df: np.ndarray) -> np.ndarray:
    """Gets the mean conductance at each step."""
    g_means = np.zeros(g_df.nano.n_steps)
    for j, df in g_df.nano.iter_dfs():
        g_means[j] = df.mean(axis=None)
    return g_means


def get_mean_curves(g_df: pd.DataFrame, keepdims=False):
    """Gets the mean conductance curve at each step."""
    if keepdims:
        mean_curves = pd.DataFrame(
            index=g_df.index, columns=g_df.columns, dtype=np.float64
        )
    else:
        mean_curves = pd.DataFrame(
            index=np.unique(g_df.index.get_level_values(0)),
            columns=g_df.columns,
            dtype=np.float64,
        )
    for j, df in g_df.nano.iter_dfs():
        if keepdims:
            mean_curves.loc[j, :] = df.mean(axis=0).to_numpy()
        else:
            mean_curves.loc[j, :] = df.mean(axis=0).to_numpy()
    return mean_curves


def get_fits(g_df: pd.DataFrame, v_ref: np.ndarray) -> list[Polynomial]:
    """Get the fits for all steps in a conductance DataFrame."""
    polynomials = []
    for j, df in g_df.nano.iter_dfs():
        g = df.to_numpy()
        v = np.tile(v_ref, g.shape[0])

        g = g.flatten()
        mask = ~np.isnan(v) & ~np.isnan(g)

        poly = Polynomial.fit(v[mask], g[mask], 1)

        # Coefficients in the unscaled voltage domain. np.polynomial.Polynomial
        # secretly converts this to the domain [-1, 1] for some reason.
        polynomials.append(poly.convert())
    return polynomials


def get_m_from_fits(polynomials: list[Polynomial]) -> np.ndarray:
    """Gets the slopes all fits."""
    m = np.zeros(len(polynomials))
    for j, p in enumerate(polynomials):
        m[j] = p.coef[1]
    return m


def get_ms(g_df: pd.DataFrame, v_ref: np.ndarray) -> np.ndarray:
    """Gets the slopes for all steps in a conductance DataFrame."""
    return get_m_from_fits(get_fits(g_df, v_ref))


def calibration_metrics(g_s: np.ndarray) -> tuple[np.floating, np.floating]:
    """Calculates the inter-quartile range (IQR) and the median for an array of conductances"""
    iqr = scipy.stats.iqr(g_s, axis=None, nan_policy="omit")
    median = np.nanmedian(g_s, axis=None)
    return iqr, median


def calibrate(g_df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Automatically calibrate a measurement to a reference.

    Calibrates a measurement to a reference inter-quartile range (IQR) and the median.
    Defaults to calibrating to the same ranges at the conductance predicted from a DNA sequence.
    (i.e. the conductances in the k-mer map of DNA for variable voltage sequencing).

    Args:
        g_df: A conductance DataFrame.
        **kwargs: Pass iqr_ref to calibrate to that IQR. Pass median_ref to calibrate to that median.
            Defaults to an IQR and median derived from the conductances retrieved using a
            predicted DNA sequence.

    """
    g_s = get_mean_curves(g_df).to_numpy()

    iqr, median = calibration_metrics(g_s)

    scale, offset = get_calibration_scale_and_offset(iqr, median, **kwargs)

    return g_df * scale + offset


def get_calibration_scale_and_offset(
    iqr: np.floating,
    median: np.floating,
    iqr_ref=DEFAULT_CALIBRATION["iqr"],
    median_ref=DEFAULT_CALIBRATION["median"],
) -> tuple[float, float]:
    """Calculate the scale and offset needed to calibrate a measurement to a reference.

    Defaults to calibrating to the same ranges at the conductance predicted from a DNA sequence.
    (i.e. the conductances in the k-mer map of DNA for variable voltage sequencing).

    Args:
        iqr: Inter-quartile range (IQR). of the measurement to be calibrated.
        median: Median of the measurement to be calibrated.
        iqr_ref: Reference IQR to calibrate to. Default to IQR of DNA prediction model.
        median_ref: Reference median to calibrate to. Default to IQR of DNA prediction model.

    Returns:
        Scale and offset needed to calibrate a measurement.

    """
    scale = iqr_ref / iqr
    offset = median_ref - scale * median

    return scale, offset
