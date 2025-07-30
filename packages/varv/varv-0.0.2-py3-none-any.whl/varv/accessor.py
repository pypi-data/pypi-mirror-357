import numpy as np
import pandas as pd

from collections.abc import Iterator, Hashable

from varv import config
from varv.config import COEF_FORMAT
from varv.feature_extraction import dimreduction


def _df_to_g_mat(df: pd.DataFrame) -> np.ndarray:
    return df.to_numpy().T


@pd.api.extensions.register_dataframe_accessor("nano")
class NanoporeAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj
        self.are_features = not isinstance(self._obj.index, pd.MultiIndex)

    @staticmethod
    def _validate(obj):
        pass

    def assert_features(self):
        if not self.are_features:
            raise AttributeError(
                "This method is only valid for DataFrames encoding features. "
                "Got a DataFrame encoding matrices with conductance half sweeps "
                "instead. To use this method, first extract features from this "
                "matrix using dimensionality reduction."
            )

    def assert_conductances(self):
        if self.are_features:
            raise AttributeError(
                "This method is only valid for DataFrames encoding matrices with "
                "conductance half sweeps at every step, got a feature DataFrame "
                "instead."
            )

    @property
    def n_features(self) -> int:
        if self.are_features:
            return len(self._obj.filter(like=COEF_FORMAT.replace("{}", "")).columns)
        else:
            return len(self._obj.columns)

    @property
    def n_steps(self) -> int:
        if self.are_features:
            return len(self._obj.index)
        else:
            return len(np.unique(self._obj.index.get_level_values(0)))

    def __len__(self) -> int:
        return self.n_steps

    @property
    def covs(self) -> pd.DataFrame:
        self.assert_features()
        return self._obj.filter(like=config.COV_FORMAT.replace("{},{}", ""))

    @property
    def coefs(self) -> pd.DataFrame:
        self.assert_features()
        return self._obj.filter(like=config.COEF_FORMAT.replace("{}", ""))

    def covs_3d(self) -> np.ndarray:
        """Gets covariances as a 3D array of shape NxDxD where N is the number of steps and D is the dimensionality features."""
        self.assert_features()
        a = self.covs.to_numpy().reshape((self.n_steps, self.n_features, self.n_features))
        # return np.transpose(a, (1, 2, 0))
        return a

    @property
    def diags(self) -> pd.DataFrame:
        self.assert_features()
        d = self.n_features
        diag_idxs = np.ravel_multi_index(np.diag_indices(d), dims=(d, d))
        return self.covs.iloc[:, diag_idxs]

    def iter_dfs(self, label=False) -> Iterator[tuple[Hashable, pd.DataFrame]]:
        """

        Args:
            label: To return the index (starting from zero), set to False.
                To instead return the actual label in the DataFrame, set to True.
        """
        self.assert_conductances()
        for j, (l, df) in enumerate(self._obj.groupby(level=0)):
            df.droplevel(0)
            yield l if label else j, df

    def get_mat(self, step: int) -> np.ndarray:
        self.assert_conductances()
        return _df_to_g_mat(self._obj.loc[step])

    def iter_matrices(self, label=False) -> Iterator[tuple[Hashable, np.ndarray]]:

        self.assert_conductances()
        for j, df in self.iter_dfs(label=label):
            df.droplevel(0)
            yield j, _df_to_g_mat(df)

    def cov(self, idx: int) -> np.ndarray:
        """Returns the covariance matrix at a location in a feature dataframe"""
        self.assert_features()
        return self.covs.loc[idx].to_numpy().reshape((self.n_features, self.n_features))

    def coef(self, idx: int) -> np.ndarray:
        """Returns the coefficients of the components at a location in a feature dataframe"""
        self.assert_features()
        return self.coefs.loc[idx].to_numpy()

    def icov(self, idx: int) -> np.ndarray:
        """Same as cov but uses purely-integer indexing like pandas.iloc"""
        return self.cov(self._obj.index[idx])

    def icoef(self, idx: int) -> np.ndarray:
        """Same as coef but uses purely-integer indexing like pandas.iloc"""
        return self.coef(self._obj.index[idx])

    def iter_covs(self) -> Iterator[tuple[int, pd.DataFrame]]:
        self.assert_features()
        for j, cov in enumerate(self.covs.to_numpy()):
            yield j, cov.reshape((self.n_features, self.n_features))

    def iter_coefs_and_covs(self):
        self.assert_features()
        ps = self.coefs.to_numpy()
        covs = self.covs.to_numpy()

        for j, (p, cov) in enumerate(zip(ps, covs)):
            yield p, cov.reshape((self.n_features, self.n_features))

    def __add__(self, offset: float):
        """Note, if features, uses default basis functions"""
        if self.are_features:
            p = dimreduction.offset_coef(offset)

            new = self._obj.copy()
            new.loc[:, self.coefs.columns] += p

            additional_cols = ["mean", "extreme"]
            for col in additional_cols:
                if col in new.columns:
                    new.loc[:, col] += offset
            return new
        else:
            return self._obj.__add__(offset)

    def __sub__(self, offset: float):
        """Note, if features, uses default basis functions"""
        return self.__add__(-offset)

    def __mul__(self, factor: float):
        if self.are_features:
            new = self._obj.copy()
            new.loc[:, self.coefs.columns] *= factor
            new.loc[:, self.covs.columns] *= factor

            additional_cols = ["std", "MSD_fit", "extreme"]
            for col in additional_cols:
                if col in new.columns:
                    new.loc[:, col] *= factor

            return new
        else:
            return self._obj.__mul__(factor)
