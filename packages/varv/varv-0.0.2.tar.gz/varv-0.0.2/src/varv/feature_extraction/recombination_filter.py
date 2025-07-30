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
import pathlib
import pickle
import warnings
from importlib import resources as impresources

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import sklearn
import tqdm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from varv import utils, config
from varv.feature_extraction import assets, dimreduction, removal_filter
from varv.utils import bhattacharyya_distance

DEFAULT_PATH = impresources.files(assets)
DEFAULT_CLF_FNAME = "recombination_clf_state_dict.zip"
DEFAULT_PREPROCESSING_PIPE_FNAME = "recombination_preprocessing_pipe.pkl"
DEFAULT_CALIBRATION_PIPE_FNAME = "recombination_calibration_pipe.pkl"


class MLP(nn.Module):
    def __init__(self, input_dim=6, hidden_dim=64, output_dim=4):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x


class TorchMLPClassifier:

    def __init__(
        self,
        input_dim=6,
        hidden_dim=64,
        output_dim=4,
        lr=0.005,
        epochs=1000,
        batch_size=64,
        device=None,
    ):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = device or (
            "mps" if torch.backends.mps.is_available() else "cpu"
        )  # For macOS
        self.model = None  # Will be initialized in fit()

        self.preprocessing_pipe = sklearn.pipeline.Pipeline(
            steps=[("scaler", StandardScaler())]
        )

        self.calibration_pipe = sklearn.pipeline.Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("logit", LogisticRegression(C=1e9) # No regularization
                    # OneVsRestClassifier(LogisticRegression(C=1e9)),
                ),
            ]
        )

    def set_model(self, state_dict=None):
        model = MLP(self.input_dim, self.hidden_dim, self.output_dim).to(self.device)
        if state_dict is not None:
            model.load_state_dict(state_dict)

        self.model = model

    def fit(self, X: np.ndarray, y: np.ndarray):

        self.set_model()

        X_train, X_calib, y_train, y_calib = sklearn.model_selection.train_test_split(
            X,
            y,
            test_size=0.2,
            shuffle=True,
            stratify=y,
        )

        self.train(X_train, y_train)

        self.calibrate(X_calib, y_calib)

        return self

    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None:
        print(f"Calibrating using {len(X)} samples.")

        logits = self.predict_logits(X)

        self.calibration_pipe.fit(logits, y)

    def predict_proba(self, X: np.ndarray):
        return self.calibration_pipe.predict_proba(self.predict_logits(X))

    def train(self, X: np.ndarray, y: np.ndarray, update_every: int = 10):

        self.preprocessing_pipe.fit(X)
        X = self.preprocessing_pipe.transform(X)

        X = torch.tensor(X, dtype=torch.float32).to(self.device)
        y = torch.tensor(y, dtype=torch.long).to(self.device)

        dataset = torch.utils.data.TensorDataset(X, y)
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True
        )

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # Training Loop
        self.model.train()
        with tqdm.tqdm(total=self.epochs) as pbar:
            for epoch in range(self.epochs):
                total_loss = 0.0
                for batch_X, batch_y in dataloader:
                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()

                if epoch % update_every == 0:
                    pbar.set_description(f"Epoch {epoch}")
                    pbar.set_postfix(loss=total_loss / len(dataloader))
                    pbar.update(update_every)

    def predict_logits(self, X):
        X = self.preprocessing_pipe.transform(X)

        self.model.eval()
        X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            outputs = self.model(X_tensor)

        return outputs.cpu().numpy()

    def predict(self, X):
        return np.argmax(self.predict_logits(X), axis=1)

    def score(self, X, y):
        predictions = self.predict(X)
        return np.mean(predictions == y)

    def save(self, path=None):
        if path is None:
            path = DEFAULT_PATH
        torch.save(self.model.state_dict(), path / DEFAULT_CLF_FNAME)

        with open(path / DEFAULT_PREPROCESSING_PIPE_FNAME, "wb") as f:
            pickle.dump(self.preprocessing_pipe, f, protocol=5)

        with open(path / DEFAULT_CALIBRATION_PIPE_FNAME, "wb") as f:
            pickle.dump(self.calibration_pipe, f, protocol=5)

    @classmethod
    def from_file(cls, path=None, device=None):
        if path is None:
            path = DEFAULT_PATH
        else:
            path = pathlib.Path(path)

        if path.is_file():
            raise ValueError(
                f"Path should point to a directory containing: {DEFAULT_CLF_FNAME} and {DEFAULT_PREPROCESSING_PIPE_FNAME}"
            )

        new = cls(device=device)
        new.set_model(torch.load(path / DEFAULT_CLF_FNAME, weights_only=True))

        new.preprocessing_pipe = get_pipe(path / DEFAULT_PREPROCESSING_PIPE_FNAME)
        new.calibration_pipe = get_pipe(path / DEFAULT_CALIBRATION_PIPE_FNAME)
        return new


def get_pipe(fname):
    with open(fname, "rb") as f:
        pipe = pickle.load(f)
    return pipe

def create_recombination_df(feature_df: pd.DataFrame) -> pd.DataFrame:
    n_features = feature_df.nano.n_features
    coef_cols = utils.get_coef_cols(n_features)
    columns = [
        ["pre"] * n_features + ["current"] * n_features,
        coef_cols * 2
    ]
    recombination_df = pd.DataFrame(index=feature_df.index[1:], columns=columns)
    recombination_df["pre"] = feature_df[coef_cols].to_numpy()[:-1, :]
    recombination_df["current"] = feature_df.loc[1:, coef_cols]

    return recombination_df



def predict_probabilities_df(recombination_df: pd.DataFrame, clf: TorchMLPClassifier = None) -> pd.DataFrame:

    if clf is None:
        clf = TorchMLPClassifier.from_file(device="cpu") # Load default classifier

    X = recombination_df.to_numpy()
    y_pred_proba = clf.predict_proba(X)

    # Piors: step, skip, back, hold

    index = [0] + recombination_df.index.to_list()
    proba_df = pd.DataFrame(index=index, columns=["step", "skip", "skip+", "back", "back+", "hold"],
                            dtype=np.float64)
    proba_df.loc[1:, ["step", "skip", "back", "hold"]] = y_pred_proba
    proba_df["skip+"] = proba_df["skip"]

    proba_df["back+"] = proba_df["back"]

    # Create scores
    proba_df.loc[:, :] = np.log(proba_df)
    return proba_df


def get_self_alignment_penalty(n_features: int = 3) -> float:
    return -0.5 * n_features

def create_transition_matrix(p: pd.Series, lookback: int = 4, penalty_sa: float = None):

    if penalty_sa is None:
        penalty_sa = get_self_alignment_penalty()

    d = lookback + 3  # Matrix dimension
    mat = np.full((d, d), np.nan, dtype=np.float64)

    forward = [p["skip"] + p["skip+"] * j for j in range(lookback - 1)]
    backward = [p["hold"]] + [p["back"] + p["back+"] * j for j in range(lookback - 1)]
    backward.reverse()
    lookback_penalty_array = np.array(backward + [p["step"]] + forward)

    for j in range(lookback):
        mat[j, :lookback] = lookback_penalty_array[lookback - j:2 * lookback - j]

    mat[lookback:, :lookback] = lookback_penalty_array[0:lookback]
    mat[-2, -1] = p["back"] + penalty_sa
    mat[:, -2] = p["skip"] + penalty_sa
    mat[:-1, -3] = p["step"] + penalty_sa

    return mat

def get_transition_matrix_df(proba_df: pd.DataFrame, penalty_sa: float = None) -> pd.DataFrame:
    lookback = 4
    new_cols = ["new_via_step", "new_via_skip", "new_via_backstep"]
    columns = list(range(-lookback, 0)) + new_cols
    index = pd.MultiIndex.from_product([proba_df.index, columns], names=["step", "from"])
    transition_matrix_df = pd.DataFrame(columns=columns, index=index, dtype=np.float64)
    transition_matrix_df.columns.name = "to"

    for (k, p) in proba_df.iterrows():
        if p.isna().all():
            continue
        transition_matrix_df.loc[k] = create_transition_matrix(p, lookback, penalty_sa)

    return transition_matrix_df


def get_distance_df(feature_df: pd.DataFrame, columns: list, lookback: int = 4, weight=0.5) -> pd.DataFrame:

    distance_df = pd.DataFrame(index=feature_df.index, columns=columns, dtype=np.float64)

    for j, (coef_ref, cov_ref) in enumerate(feature_df.nano.iter_coefs_and_covs()):
        for k in range(0, lookback):
            idx = j - lookback + k
            if 0 <= idx < len(feature_df):
                distance = bhattacharyya_distance(
                    feature_df.nano.icoef(idx),
                    feature_df.nano.icov(idx),
                    coef_ref,
                    cov_ref)
                distance_df.iloc[j, k] = -distance

    distance_df.iloc[:, lookback:] = 0  # Self is always distance 9

    return distance_df * weight

def get_alignment_table(distance_df: pd.DataFrame, transition_matrix_df: pd.DataFrame, lookback: int = 4) -> pd.DataFrame:
    alignment_table = pd.DataFrame(index=distance_df.index, columns=distance_df.columns, dtype=np.float64)
    alignment_table.iloc[0, lookback] = 0

    for j, (_, transition_matrix) in enumerate(transition_matrix_df.groupby(level=0)):
        if j == 0:
            continue

        transition_matrix = transition_matrix.droplevel(0)

        row_prev = alignment_table.iloc[j - 1]
        distances = distance_df.iloc[j]
        alignment_table.iloc[j, :] = (transition_matrix + distances).add(row_prev, axis=0).max(axis=0)


    return alignment_table


class RecombinationFilter:

    def __init__(self, lookback: int = 4, clf_path=None, max_iter: int = 10, verbose: bool = False):
        self.lookback = lookback
        self.penalty_sa = None
        self.clf_path = clf_path
        self.max_iter = max_iter
        self.verbose = verbose

        self._alignment_table = None
        self.g_df = None
        self.feature_df = None

    def get_transition_matrices(self) -> pd.DataFrame:
        recombination_df = create_recombination_df(self.feature_df)

        clf = TorchMLPClassifier.from_file(self.clf_path)

        proba_df = predict_probabilities_df(recombination_df, clf)

        return get_transition_matrix_df(proba_df, self.penalty_sa)

    def align(self) -> None:

        assert self.g_df is not None

        self.feature_df = removal_filter.preprocess(self.g_df, unfray=False)

        transition_matrix_df = self.get_transition_matrices()

        distance_df = get_distance_df(
            self.feature_df,
            columns=transition_matrix_df.columns,
            lookback=self.lookback
        )

        self._alignment_table = get_alignment_table(
            distance_df,
            transition_matrix_df
        )

        self.feature_df["alignment"] = self._alignment_table.idxmax(axis=1)
        add_step_sequence(self._alignment_table, self.feature_df)

    def combine(self) -> int:
        changes = 0
        new_steps_level = self.g_df.index.get_level_values(0).to_numpy()
        for j, (idx, alignment) in enumerate(zip(self.feature_df.index, self.feature_df["alignment"])):
            if "new" in str(alignment):
                new_idx = idx
            else:
                back = int(alignment)
                new_idx = self.feature_df.index[j + back]  # Already negative

                changes += 1

            new_steps_level[new_steps_level == idx] = new_idx

        if self.verbose:
            print(f"Applied {changes} changes")

        period_counter = {step: 0 for step in np.unique(new_steps_level)}
        periods_level = np.zeros_like(new_steps_level, dtype=int)

        for j, step in enumerate(new_steps_level):
            periods_level[j] = period_counter[step]
            period_counter[step] += 1

        index = pd.MultiIndex.from_tuples(tuple(zip(new_steps_level, periods_level)), names=["step", "period"])
        g_df_recombined = self.g_df.copy()
        g_df_recombined.index = index

        self.g_df = g_df_recombined

        return changes

    def iter_recombine(self, g_df: pd.DataFrame):
        g_df.nano.assert_conductances()
        self.g_df = g_df.copy()
        n_steps_original = self.g_df.shape[0]

        for j in range(self.max_iter):
            self.align()

            yield self.g_df, self.feature_df

            changes = self.combine()

            if not changes:
                break

            if self.g_df.nano.n_steps == 1:
                warnings.warn(f"Recombination filter started with {n_steps_original} steps but removed to <= 1.")
                yield None, None
                break

    def fit(self, g_df: pd.DataFrame):
        for _ in self.iter_recombine(g_df):
            pass

    def predict(self):
        return self.g_df

    def predict_features(self):
        return self.feature_df

def get_step_sequence(alignment_table: pd.DataFrame) -> np.ndarray:
    """Calculates step sequence. Negative numbers are backsteps, 0 is hold, 1 is step, 2 is skip"""
    alignment_table.idxmax(axis=1)

    alignments = alignment_table.idxmax(axis=1)
    alignments[alignments == "new_via_step"] = 0
    alignments[alignments == "new_via_backstep"] = -1
    alignments[alignments == "new_via_skip"] = 1

    step_seq = alignments.to_numpy(dtype=np.float64)

    step_seq = np.concatenate([[0], np.diff(step_seq)])
    step_seq += 1
    step_seq[step_seq > 1] = 1  # Turn steps back into sequence into normal steps
    step_seq[alignments == 1] = 2  # Add back skips

    return step_seq

def add_step_sequence(alignment_table: pd.DataFrame, feature_df: pd.DataFrame) -> pd.DataFrame:
    seq = get_step_sequence(alignment_table)

    feature_df["step_type"] = "-"

    feature_df.loc[seq < 0, "step_type"] = "back"
    feature_df.loc[seq == 0, "step_type"] = "hold"
    feature_df.loc[seq == 1, "step_type"] = "step"
    feature_df.loc[seq == 2, "step_type"] = "skip"

    feature_df["step_type"] = feature_df["step_type"].astype("category")

    return feature_df

def marker(ax, x, s, y=0.9, size=15, alpha=0.2, scale=1):
    """y in axes coordinates"""
    y_lim = ax.get_ylim()

    ax.text(x, y * (y_lim[1] - y_lim[0]) + y_lim[0], s, size=size * scale, ha="center", va="center",
            fontname="Hiragino Sans")
    ax.axvline(x, 0, y - size * 0.005, zorder=-100, alpha=alpha)
    ax.axvline(x, y + size * 0.005, 1, zorder=-100, alpha=alpha)


def step(*args, **kwargs):
    marker(*args, u"\u25B6", **kwargs)


def back(*args, n=1, **kwargs):
    marker(*args, n * u"\u25C0", scale=0.66 ** (n - 1), **kwargs)


def skip(*args, **kwargs):
    marker(*args, u"\u25B6\u25B6", scale=0.66, **kwargs)


def hold(*args, **kwargs):
    marker(*args, u"\u0131\u0131", scale=1.5, **kwargs)


def plot_recombination(
        feature_df: pd.DataFrame,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        iconsize: float = 15,
        room=0.25,
        **kwargs):

    drawers = {
        "hold": hold,
        "step": step,
        "skip": skip,
        "back": back,
    }

    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE)

    fig, ax = dimreduction.plot_feature_df(feature_df, fig=fig, ax=ax, **kwargs)
    ylim = ax.get_ylim()
    y_size = ylim[1] - ylim[0]
    ax.set_ylim(top=ylim[1] + y_size * room )

    step_seq = feature_df["step_type"]

    for j, step_type in enumerate(step_seq):
        drawer = drawers[step_type]
        drawer(ax, j + 0.5, size=iconsize)