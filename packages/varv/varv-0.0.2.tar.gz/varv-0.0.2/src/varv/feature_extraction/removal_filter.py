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
import pickle
import warnings
from importlib import resources as impresources
import numpy as np
import pandas as pd
import sklearn

from varv.classification import predictdna
from varv.feature_extraction import assets, dimreduction
from varv import config, utils
from varv.preprocessing import capnorm

DEFAULT_PATH = impresources.files(assets)
DEFAULT_PIPE_FNAME = "removal_svm.pkl"


def score_feature_df(feature_df: pd.DataFrame, model_df: pd.DataFrame) -> pd.DataFrame:

    if model_df is None:
        model_df = predictdna.DNA_MODEL

    scores = get_scores(feature_df, model_df)

    feature_df["score"] = np.max(scores, axis=0)

    return feature_df


def get_scores(feature_df, model_df):
    mu = feature_df.nano.coefs.to_numpy()
    sigma = feature_df.nano.covs_3d()

    mu_ref = model_df.nano.coefs.to_numpy()[:, np.newaxis, :]
    sigma_ref = model_df.nano.covs_3d()[:, np.newaxis, ...]

    # Vectorized calculation of pairwise distances
    scores = utils.bhattacharyya_distance(mu, sigma, mu_ref, sigma_ref)

    with np.errstate(divide="ignore"):
        scores = -np.log(scores)

    return -scores


def removal_features(feature_df: pd.DataFrame) -> pd.DataFrame:
    coef_columns = list(feature_df.filter(like=config.COEF_FORMAT.replace("{}", "")).columns)
    n = feature_df.nano.n_features
    columns = [
        ["pre"] * n + ["current"] * n + ["post"] * n + ["properties"] * 3,
        coef_columns * 3 + ["feature_10", "feature_11", "dna_score"],
    ]

    removal_df = pd.DataFrame(columns=columns, index=feature_df.index, dtype=np.float64)

    # Everything but the ends filled in with coefs before and after
    index = feature_df.index
    removal_df.loc[index[1:], "pre"] = feature_df.loc[index[:-1]].nano.coefs.to_numpy()
    removal_df.loc[:, "current"] = feature_df.nano.coefs.to_numpy()
    removal_df.loc[index[:-1], "post"] = feature_df.loc[index[1:]].nano.coefs.to_numpy()

    # First measurement uses its own value as pre, as if its is a perfect backstep. Same for last step.
    removal_df.loc[index[0], "pre"] = feature_df.nano.coefs.to_numpy()[0]
    removal_df.loc[index[-1], "post"] = feature_df.nano.coefs.to_numpy()[-1]

    # Properties just copied over
    removal_df[("properties", "feature_10")] = feature_df["extreme"] / np.sqrt(
        feature_df["n_samples"]
    )
    removal_df[("properties", "feature_11")] = feature_df["MSD_fit"] / np.sqrt(
        feature_df["n_samples"]
    )
    removal_df[("properties", "dna_score")] = feature_df["dna_score"]

    return removal_df


def preprocess(g_df: pd.DataFrame, unfray=True) -> pd.DataFrame:
    g_df_norm = capnorm.normalize(g_df)
    if unfray:
        g_df_norm = capnorm.fraying_correction(g_df_norm)
    g_df_norm = capnorm.calibrate(g_df_norm)
    feature_df = dimreduction.get_feature_df(g_df_norm)
    feature_df = dimreduction.fill_ill_defined_covs(feature_df)
    return feature_df


class RemovalFilter:

    def __init__(
        self,
        threshold: float = 0.9,
        model_df: pd.DataFrame = None,
        pipe: sklearn.pipeline.Pipeline = None,
        verbose: bool = False,
        max_iter: int = 10,
        min_steps_unfray: int = 30,
        end_drop: bool = True,
    ):

        self.threshold = threshold
        self.dna_scores_df = None
        self.model_df = model_df
        self.pipe = pipe
        self.verbose = verbose
        self.max_iter = max_iter
        self.min_steps_unfray = min_steps_unfray

        self.g_df = None
        self.feature_df = None

        if self.model_df is None:
            self.model_df = predictdna.DNA_MODEL

        if self.pipe is None:
            with open(DEFAULT_PATH / DEFAULT_PIPE_FNAME, "rb") as f:
                self.pipe = pickle.load(f)

    def iter_removal(self, g_df: pd.DataFrame):
        g_df.nano.assert_conductances()
        self.g_df = g_df.copy()
        n_steps_original = g_df.shape[0]

        for j in range(self.max_iter):
            self.feature_df = preprocess(self.g_df, unfray=False)

            if j == 0:  # Only calculate first time round
                self.calculate_dna_scores(self.feature_df)

            self.feature_df["dna_score"] = self.dna_scores_df["dna_score"]

            removal_df = removal_features(self.feature_df)

            score = self.score_with_pipeline(removal_df)

            self.feature_df["removal_score"] = score

            yield self.g_df, self.feature_df

            remove = removal_df.iloc[score > self.threshold].index

            if self.verbose:
                print(f"Removed {len(remove)} steps.")

            if not len(remove):
                break

            self.g_df.drop(index=remove, inplace=True, level=0)
            self.dna_scores_df.drop(index=remove, inplace=True)

            if self.g_df.nano.n_steps == 1:
                warnings.warn(f"Removal filter started with {n_steps_original} steps but removed to <= 1.")
                yield None, None
                break

    def fit(self, g_df: pd.DataFrame):
        for _ in self.iter_removal(g_df):
            pass

    def predict(self) -> pd.DataFrame:
        if self.dna_scores_df is None:
            raise ValueError("Fit removal filter before getting results.")
        return self.g_df.copy()

    def predict_features(self) -> pd.DataFrame:
        if self.dna_scores_df is None:
            raise ValueError("Fit removal filter before getting results.")
        return self.feature_df.copy()

    def score_with_pipeline(self, removal_df):
        return self.pipe.predict_proba(removal_df.to_numpy())[:, 1]

    def calculate_dna_scores(self, feature_df):
        dna_scores = get_scores(feature_df, self.model_df)
        dna_scores = np.max(dna_scores, axis=0)
        self.dna_scores_df = pd.DataFrame(data=dna_scores, columns=["dna_score"])
