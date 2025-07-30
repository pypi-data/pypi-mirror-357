import json
import pathlib

import numpy as np
import pandas as pd

from varv import base, events, utils

META_FILENAME = "metadata.json"
ANNOTATION_FILENAME = "annotations.csv"


class EventDataset:
    """Load dataset of events containing current and voltage data"""

    def __init__(self, reads_dir, annotations_file=None):
        self.reads_dir = pathlib.Path(reads_dir)

        if annotations_file is None:
            annotations_file = self.reads_dir / ANNOTATION_FILENAME
        self.annotations = pd.read_csv(annotations_file)

        with open(self.reads_dir / META_FILENAME) as f:
            meta = json.load(f)

        sfreq = meta.pop("sfreq")
        self.info = base.Info(sfreq, name="", **meta)

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        path = self.reads_dir / self.annotations.iloc[idx, 0]
        data = np.load(path)

        data = pd.DataFrame(
            {
                "i": data["i"],
                "v": data["v"],
            }
        )
        eve = events.Event(self.info, data)
        variant = self.annotations.iloc[idx, 1]

        return eve, variant


G_FORMAT = "g_df_{:06d}.csv"
FEAT_FORMAT = "feature_df_{:06d}.csv"
class TablesDataset:
    """Load dataset of events as tables containing conductance matrices and feature matrices"""

    def __init__(self, reads_dir, annotations_file=None):
        self.reads_dir = pathlib.Path(reads_dir)

        if annotations_file is None:
            annotations_file = self.reads_dir / ANNOTATION_FILENAME
        self.annotations = pd.read_csv(annotations_file, index_col=0)

    @classmethod
    def from_iterator(cls, reads_dir, iterator):
        reads_dir = pathlib.Path(reads_dir)
        reads_dir.mkdir(parents=True, exist_ok=True)

        all_metadata = None
        for j, (g_df, feature_df, metadata) in enumerate(iterator()):
            g_df_fname = G_FORMAT.format(j)
            feature_df_fname = FEAT_FORMAT.format(j)

            if all_metadata is None:
                all_metadata = {k: [v] for k, v in metadata.items()}

                all_metadata["g_df_fname"] = [g_df_fname]
                all_metadata["feature_df_fname"] = [feature_df_fname]
            else:
                for k, v in metadata.items():
                    all_metadata[k].append(v)

                all_metadata["g_df_fname"].append(g_df_fname)
                all_metadata["feature_df_fname"].append(feature_df_fname)

            g_df = pd.DataFrame(g_df)
            feature_df = pd.DataFrame(feature_df)

            g_df.to_csv(reads_dir / g_df_fname)
            feature_df.to_csv(reads_dir / feature_df_fname)

        annotations = pd.DataFrame(all_metadata)
        annotations.to_csv(reads_dir / ANNOTATION_FILENAME)

        return cls(reads_dir)

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        g_df_fname = self.reads_dir / self.annotations.loc[idx, "g_df_fname"]
        feature_df_fname = self.reads_dir / self.annotations.loc[idx, "feature_df_fname"]

        g_df = pd.read_csv(g_df_fname, index_col=[0, 1])
        feature_df = pd.read_csv(feature_df_fname, index_col=0)

        variant = self.annotations.loc[idx, "variant"]

        return g_df, feature_df, variant

class ReferenceTablesDataset:
    """Dataset from data in Noakes 2019, used as reference"""

    def __init__(self, reads_dir, annotations_file=None):
        self.reads_dir = pathlib.Path(reads_dir)

        if annotations_file is None:
            annotations_file = self.reads_dir / ANNOTATION_FILENAME
        self.annotations = pd.read_csv(annotations_file)

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        path = self.reads_dir / self.annotations.iloc[idx, 0]
        data = np.load(path)

        features = data["p"].T
        g_df = data["g"].T

        steps = pd.DataFrame(features, columns=utils.get_coef_cols(3))

        index = pd.MultiIndex.from_product(
            [np.arange(len(features)), [0]], names=["step", "period"]
        )
        columns = [f"g_{j}" for j in range(g_df.shape[1])]
        g_df = pd.DataFrame(g_df, index=index, columns=columns)

        variant = self.annotations.iloc[idx, 1]

        return steps, g_df, variant

