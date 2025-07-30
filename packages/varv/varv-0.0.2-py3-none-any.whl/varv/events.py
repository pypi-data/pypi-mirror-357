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
import os
import copy
import pathlib
import queue
import typing
import itertools
import multiprocessing as mp
from collections.abc import Callable

import h5py
import tqdm
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from varv import utils, base, config
from varv.feature_extraction import dimreduction
from varv.preprocessing import changepoint, eventdetection, changepoint_cv

EVENT_NUMBER_ATTR_NAME = "num"
LABEL_ATTR_NAME = "label"
OPEN_PORE_CURRENT_ATTR_NAME = "ios"

EVENT_GROUP_NAME = "Event_{:06}"


def _get_event_data_group_name(num=None):
    if num is not None:
        return EVENT_GROUP_NAME.format(num)
    else:
        return EVENT_GROUP_NAME.split("_{")[0]


class Event(base.Data):

    _fname_format = "{}_eve.h5"
    _steps_database_name = "Steps"  # Should be the same as Events

    def __init__(
        self,
        info: base.Info,
        data: pd.DataFrame,
        steps: typing.Optional[pd.DataFrame] = None,
        num: int = None,
        label: int = None,
        ios: float = None,
        channel: int = None,
        start_idx: int = None,
        on_disk: typing.Union[bool, str, pathlib.Path] = False,
    ):
        # Init subclasses in memory
        super().__init__(info, data, False, channel, start_idx)

        self._steps = steps
        self._num = num
        self._label = label
        self._ios = ios

        # Override group name
        self._set_data_group_name("Event")

        # Save to disk if needed
        self._set_disk(on_disk)
        if on_disk:
            self._save_from_memory_to_file(self.on_disk)
            self._erase_memory()

    def __repr__(self):
        table = self.info.as_dict()
        table["on_disk"] = bool(self.on_disk)
        table["channel"] = self.channel
        table["start_idx"] = self.start_idx
        table["num"] = self.num
        table["label"] = self.label
        table["ios"] = self.ios
        table = {k: str(v) for k, v in table.items() if v is not None}
        message = " ".join([f"{k}=" + "{" + k + "}," for k in table.keys()])
        return f"{self.__class__.__name__}({message.format(**table)})"

    def __str__(self):
        df = self.info.as_dataframe()
        df_dur = pd.DataFrame(
            [
                [f"{self.label}"],
            ],
            columns=[""],
        )
        df_dur.index = ["Label"]
        df = pd.concat([df, df_dur])
        return df.__str__()

    @property
    def label(self) -> np.int32:
        return self._get_attr(LABEL_ATTR_NAME)

    @label.setter
    def label(self, value: np.int32):
        self._set_attr(LABEL_ATTR_NAME, value)

    @property
    def num(self) -> np.int32:
        return self._get_attr(EVENT_NUMBER_ATTR_NAME)

    @num.setter
    def num(self, value: np.int32):
        self._set_attr(EVENT_NUMBER_ATTR_NAME, value)

    @property
    def ios(self) -> np.float64:
        return self._get_attr(OPEN_PORE_CURRENT_ATTR_NAME)

    @ios.setter
    def ios(self, value: float):
        self._set_attr(OPEN_PORE_CURRENT_ATTR_NAME, value)

    @property
    def steps(self) -> pd.DataFrame | None:
        if self.on_disk:
            if self._steps_database_name in self._handle[self._data_group_name]:
                arr = self._handle[self._steps_path][()]
                return utils.df_from_struct(arr)
            else:
                return None
        else:
            return self._steps

    @steps.setter
    def steps(self, df: pd.DataFrame):
        if self.on_disk:
            if self._steps_database_name in self._handle[self._data_group_name]:

                del self._handle[self._steps_path]

                if df is not None:
                    self._handle[self._data_group_name].create_dataset(
                        self._steps_database_name, data=utils.struct_from_df(df)
                    )
            else:
                if df is not None:
                    self._handle[self._data_group_name].create_dataset(
                        self._steps_database_name, data=utils.struct_from_df(df)
                    )
        else:
            self._steps = df

    def _erase_memory(self):
        super()._erase_memory()
        self._num = None
        self._label = None
        self._ios = None
        self._steps = None

    def _get_save_fname(self):
        s = str(self.info.name)
        if self.num is not None:
            s += f"_{self.num:06}"
        return self._fname_format.format(s)

    def _save_from_memory_to_file(self, fname):
        super()._save_from_memory_to_file(fname)  # Already writes raw database

        attrs = {
            OPEN_PORE_CURRENT_ATTR_NAME: self._ios,
            EVENT_NUMBER_ATTR_NAME: self._num,
            LABEL_ATTR_NAME: self._label,
        }
        self._write_attrs(**attrs)

        if self._steps is not None:
            databases = {self._steps_database_name: self._steps}
            self._write_databases(**databases)

    def _set_data_group_name(self, name: str):
        super()._set_data_group_name(name)
        self._steps_path = f"/{name}/{self._steps_database_name}"

    def clear_steps(self):
        self.steps = None

    def find_steps(
        self,
        **kwargs,
    ):
        if self.is_varv():
            self.steps = changepoint.get_step_df(
                self.i,
                self.v,
                self.info.sfreq,
                self.get_bv_period(),
                **kwargs,
            )

        else:
            self.steps = changepoint_cv.get_step_df(self.i, self.info.sfreq, **kwargs)

    def get_bv_period(self) -> int:
        return int(self.info.sfreq / self.info.bfreq)

    def plot(
        self,
        field="i",
        fmt="-",
        *args,
        start: float = None,
        stop: float = None,
        lowpass=None,
        savefig=None,
        fig=None,
        ax=None,
        show_open_pore_current=False,
        line_at_step=False,
        **kwargs,
    ):
        """

        Args:
            *args:
            field:
            start:
            stop:
            lowpass:
            savefig:
            fig:
            ax:
            **kwargs:

        Returns:

        """
        ax, field, fig, start, stop = self._plot_init(field, start, stop, fig, ax)

        if "alpha" not in kwargs:
            alpha = 1 if self.steps is None else 0.5
        else:
            alpha = kwargs.pop("alpha")

        x = self.get_time(start=start, stop=stop)
        as_ms = x[-1] - x[0] < 1

        x = self.get_time()[start:stop]
        y = self[field, start:stop]

        if lowpass:
            y = utils.lowpass_filter(y, self.info.sfreq, lowpass)

        ax.plot(x, y, **kwargs)

        if as_ms:
            xticks = ax.get_xticks()
            ax.set_xticks(xticks, [f"{x:0.0f}" for x in xticks * 1000])

        ax.set_xlabel(f'$t$ ({"ms" if as_ms else "s"})', fontsize=14)
        ax.set_ylabel(base.Y_LABELS[field], fontsize=14)

        if self.info.ios and show_open_pore_current:
            color = "grey"
            ax.axhline(self.info.ios, color=color, label="Open pore current")

            if isinstance(show_open_pore_current, tuple):
                lines = ["--", "-.", ":"]
                linecycler = itertools.cycle(lines)

                for percentage in show_open_pore_current:
                    ax.axhline(
                        self.info.ios * percentage,
                        color=color,
                        linestyle=next(linecycler),
                        alpha=0.5,
                        label=f"{percentage:.0%}",
                    )

                ax.axhspan(
                    self.info.ios * min(show_open_pore_current),
                    self.info.ios * max(show_open_pore_current),
                    color=color,
                    alpha=0.05,
                )

            ax.legend(loc="upper right")

        title = self.info.name + "\nEvent"
        if self.num is not None:
            title += f" {self.num}"

        ax.set_title(title)

        self._end_plot(fig, savefig)

        return fig, ax

    def plot_steps(
        self,
        fig: plt.Figure = None,
        ax: plt.Axes = None,
        **kwargs,
    ):
        if self.is_varv():

            fig, ax = dimreduction.plot_feature_df(self.steps, fig=fig, ax=ax, **kwargs)

            title = self.info.name + "\nEvent"
            if self.num is not None:
                title += f" {self.num}"

            ax.set_title(title)

            return fig, ax
        else:
            raise NotImplementedError()

    def to_memory(self):
        if self.on_disk:
            self._num = self.num
            self._steps = self.steps
            self._ios = self.ios
            self._label = self.label

        super().to_memory()  # Deletes file handle after wards


def data_generator(raw: base.Raw, properties: pd.DataFrame, ios_arr: np.ndarray):
    mean_ios_arr = [None] * len(properties)
    data = []
    for i, row in properties.iterrows():
        start = int(row["start_idx"])
        end = int(row["stop_idx"])

        df = raw[start:end]
        assert isinstance(df, pd.DataFrame)

        if ios_arr is not None:
            mean_ios_arr[i] = np.mean(ios_arr[[start, end]])

        df.reset_index(drop=True, inplace=True)
        data.append(df)

    return data, mean_ios_arr


def add_event_time(properties, sfreq):
    properties["start_s"] = properties["start_idx"] / sfreq
    properties["stop_s"] = properties["stop_idx"] / sfreq
    properties["dur_s"] = properties["n_samples"] / sfreq


def copy_attr_to_hdf(df, event_group, attr, strict=True):
    if strict or hasattr(df, attr):
        event_group.attrs[attr] = getattr(df, attr)


def _clean_array(l: list, dtype=float) -> list:
    if isinstance(l, (int, float, np.integer, np.floating)):
        l = [l]
    return [None if item is None or np.isnan(item) else dtype(item) for item in l]


def _get_pandas_slice(index):
    if isinstance(index, slice) and index.stop is not None:  # Skip all slice
        index = slice(index.start, index.stop - 1, index.step)
    return index


def _ensure_slice(index):
    """Get slice from single index, if needed."""
    if isinstance(index, int):
        index = slice(index, index + 1)
    return index


class AttributeProxy:
    def __init__(
        self,
        event_group_names: list,
        name: str,
        set_data_group_name: Callable,
        get_attr: Callable,
        set_attr: Callable,
        strict: bool = False,
        dtype=float,
    ):
        self._event_group_names = event_group_names
        self._name = name
        self._set_data_group_name = set_data_group_name
        self._get_attr = get_attr
        self._set_attr = set_attr
        self._strict = strict
        self._dtype = dtype

    def __getitem__(self, index):
        group_names = self._check_slicing(index)

        attrs = []
        for i, group_name in enumerate(group_names):
            self._set_data_group_name(group_name)
            attrs.append(self._get_attr(self._name, on_disk=True, strict=self._strict))

        self._set_data_group_name("None")

        attrs = _clean_array(attrs, dtype=self._dtype)

        if len(attrs) == 1:
            return attrs[0]
        else:
            return attrs

    def _check_slicing(self, index):
        group_names = self._event_group_names[index]
        if isinstance(index, int):
            group_names = [group_names]
        elif not isinstance(index, slice):
            raise IndexError(f"Index {index} must be int or slice")
        return group_names

    def __setitem__(self, index, value):
        group_names = self._check_slicing(index)

        if isinstance(value, (int, float, np.integer, np.floating)):
            value = [value] * len(group_names)

        for val, group_name in zip(value, group_names):
            self._set_data_group_name(group_name)
            self._set_attr(self._name, val, on_disk=True, strict=self._strict)

        self._set_data_group_name("None")

    def __len__(self):
        return len(self._event_group_names)

    def __repr__(self):
        return repr(list(self))


def _none_list_if_none(attr, n: int) -> list:
    if attr is None:
        attr = [None] * n
    return attr


def filter_list_by_mask(l: list, mask):
    return list(itertools.compress(l, mask))


class Events(base.BaseData):

    _fname_format = "{}_eves.h5"
    _properties_database_name = "Properties"
    _steps_database_name = "Steps"

    def __init__(
        # TODO: put info first
        self,
        data: list[pd.DataFrame],
        info: base.Info,
        properties: pd.DataFrame,
        steps: typing.List[pd.DataFrame] = None,
        nums: list[int] | np.ndarray = None,
        labels: list[int] | np.ndarray = None,
        ioss: list[float] | np.ndarray = None,
        channels: list[int] | np.ndarray = None,
        start_idxs: list[int] | np.ndarray = None,
        on_disk: bool | pathlib.Path = False,
    ):
        if len(data) != len(properties):
            raise ValueError(
                "Length of the data does not match the length of properties "
                "DataFrame."
            )
        for df in data:
            assert base.CURRENT_FIELD_NAME in df.columns
            assert base.VOLTAGE_FIELD_NAME in df.columns

        super().__init__(info, False)

        # HDF properties
        self._event_group_names = []
        self._properties_database_name = "Properties"

        # Data in memory
        self._data = data
        self._properties = properties

        n = len(data)
        self._steps = _none_list_if_none(steps, n)
        self._nums = _none_list_if_none(nums, n)
        self._labels = _none_list_if_none(labels, n)
        self._ioss = _none_list_if_none(ioss, n)
        self._channels = _none_list_if_none(channels, n)
        self._start_idxs = _none_list_if_none(start_idxs, n)

        # Save to disk if needed
        self._set_disk(on_disk)
        if on_disk:
            self._save_from_memory_to_file(self.on_disk)
            self._erase_memory()

    @property
    def channels(self):
        return self._get_attrs(base.CHANNEL_ATTR_NAME, dtype=int)

    @channels.setter
    def channels(self, value):
        self._set_attrs(base.CHANNEL_ATTR_NAME, value)

    @property
    def start_idxs(self):
        return self._get_attrs(base.START_IDX_ATTR_NAME, dtype=int)

    @start_idxs.setter
    def start_idxs(self, value):
        self._set_attrs(base.START_IDX_ATTR_NAME, value)

    @property
    def nums(self):
        return self._get_attrs(EVENT_NUMBER_ATTR_NAME, dtype=int)

    @nums.setter
    def nums(self, value):
        self._set_attrs(EVENT_NUMBER_ATTR_NAME, value)

    @property
    def labels(self):
        return self._get_attrs(LABEL_ATTR_NAME, dtype=int)

    @labels.setter
    def labels(self, value):
        self._set_attrs(LABEL_ATTR_NAME, value)

    @property
    def ioss(self):
        return self._get_attrs(OPEN_PORE_CURRENT_ATTR_NAME)

    @ioss.setter
    def ioss(self, value):
        self._set_attrs(OPEN_PORE_CURRENT_ATTR_NAME, value)

    def _save_from_memory_to_file(self, fname):
        self._handle = h5py.File(fname, "w")
        self.info.set_and_write_handle(self._handle)

        # Save properties
        self._handle.create_dataset(
            self._properties_database_name, data=utils.struct_from_df(self._properties)
        )

        # Save each event
        for i, data in enumerate(self._data):

            # Create group
            group_name = _get_event_data_group_name(i)
            self._event_group_names.append(group_name)
            self._handle.create_group(group_name)

            # Set path to data. Point to the next event each time.
            self._set_data_group_name(group_name)

            # Write attributes
            attrs = {
                EVENT_NUMBER_ATTR_NAME: self._nums,
                LABEL_ATTR_NAME: self._labels,
                OPEN_PORE_CURRENT_ATTR_NAME: self._ioss,
                base.CHANNEL_ATTR_NAME: self._channels,
                base.START_IDX_ATTR_NAME: self._start_idxs,
            }
            attrs = {k: v[i] for k, v in attrs.items() if v is not None}
            self._write_attrs(**attrs)

            # Write databases
            databases = {self._raw_database_name: data}
            if self._steps[i] is not None:
                databases[self._steps_database_name] = self._steps[i]
            self._write_databases(**databases)

        # Reset path data to data
        self._set_data_group_name("None")

    def _erase_memory(self):
        self._steps = None
        self._data = None
        self._properties = None
        self._nums = None
        self._labels = None
        self._ioss = None
        self._channels = None
        self._start_idxs = None

    def _get_attrs(self, name, on_disk: bool = None, strict: bool = False, dtype=float):
        on_disk = self.on_disk if on_disk is None else self.on_disk

        if on_disk:
            return AttributeProxy(
                self._event_group_names,
                name,
                self._set_data_group_name,
                self._get_attr,
                self._set_attr,
                strict=strict,
                dtype=dtype,
            )
        else:
            return getattr(self, self._get_memory_attr_name(name))

    def _set_attrs(
        self, name, values, on_disk: bool = None, strict: bool = False
    ) -> None:
        on_disk = self.on_disk if on_disk is None else self.on_disk
        if isinstance(values, (int, float)):
            values = [values] * len(self)
        elif len(values) != len(self):
            raise ValueError(
                "Length of the new values does not match the length of events."
            )
        if on_disk:
            for value, group_name in zip(values, self._event_group_names):
                self._set_data_group_name(group_name)
                self._set_attr(name, value, on_disk=True, strict=strict)

            self._set_data_group_name("None")
        else:
            setattr(self, self._get_memory_attr_name(name), values)

    @staticmethod
    def _get_memory_attr_name(name):
        return f"_{name}s"

    def _copy_to_new_file(self, fname):
        with h5py.File(fname, "w") as handle_dest:
            self._handle.copy(
                self._handle[self._info_group_name], handle_dest, self._info_group_name
            )
            self._handle.copy(
                self._handle[self._properties_database_name],
                handle_dest,
                self._properties_database_name,
            )

            for group in self._event_group_names:
                self._handle.copy(self._handle[group], handle_dest, group)

    def __len__(self):
        if self.on_disk:
            return len(self._event_group_names)
        else:
            return len(self._properties)

    def _get_group_names(self):
        find = EVENT_GROUP_NAME.split("{")[0]
        return [key for key in self._handle.keys() if find in key]

    def __add__(self, other):
        if isinstance(self, EmptyEvents):
            return other
        elif isinstance(other, EmptyEvents):
            return self
        elif isinstance(self, Events) and isinstance(other, Events):
            other.reassign_event_numbers(offset=len(self))
            if self.on_disk:
                tmp = False
                if not other.on_disk:
                    tmp = True
                    other.to_disk("tmp.h5")
                self.properties = pd.concat([self.properties, other.properties], axis=0)

                # Copy over data
                n = len(self)
                new_group_names = [
                    _get_event_data_group_name(i) for i in range(n, n + len(other))
                ]
                for group, new_group in zip(other._event_group_names, new_group_names):
                    other._handle.copy(other._handle[group], self._handle, new_group)

                self._event_group_names = self._event_group_names + new_group_names

                # Check unique
                assert sorted(set(self._event_group_names)) == sorted(
                    self._event_group_names
                )

                if tmp:
                    os.remove("tmp.h5")
            else:
                if other.on_disk:
                    other.to_memory()

                self._properties = pd.concat(
                    [self.properties, other.properties], axis=0
                )
                self._data += other._data
                self._steps += other._steps

            return self
        else:
            raise TypeError(
                f"Cannot concatenate object of type "
                f"{type(self)} with object of type {type(other)}."
            )

    def __getitem__(self, item):
        if isinstance(item, (int, np.integer)):
            info = self.info.copy()
            return Event(
                info,
                self.data[item],
                self.steps[item],
                self.nums[item],
                self.labels[item],
                self.ioss[item],
                self.channels[item],
                self.start_idxs[item],
                on_disk=False,
            )
        else:
            # Get mask
            idxs = np.arange(len(self))[item]
            mask = np.zeros(len(self), dtype=bool)
            mask[idxs] = True

            return self.filter_by_mask(mask, inplace=False)

    @property
    def properties(self):
        if self.on_disk:
            return utils.df_from_struct(
                self._handle[self._properties_database_name][()]
            )
        else:
            return self._properties

    @properties.setter
    def properties(self, df: pd.DataFrame):
        if self.on_disk:
            if df.shape != self.properties.shape:
                del self._handle[self._properties_database_name]

                self._handle.create_dataset(
                    self._properties_database_name, data=utils.struct_from_df(df)
                )
            else:
                self._handle[self._properties_database_name][()] = utils.struct_from_df(
                    df
                )
        else:
            self._properties = df

    def _get_database_from_all_groups(self, name: str, strict=True):
        dfs = []
        for i in range(len(self)):
            dfs.append(self._get_database(i, name, strict))
        return dfs

    def _get_database(self, item: int, name: str, strict=True) -> pd.DataFrame | None:
        group_name = self._event_group_names[item]
        group = self._handle[group_name]
        if strict or name in group:
            arr = group[name][()]
            return utils.df_from_struct(arr)
        else:
            return None

    def _set_database_for_all_groups(self, name: str, dfs, strict=True):
        for i, df in enumerate(dfs):
            self._set_database(i, name, df, strict)

    def _set_database(
        self, item: int, name: str, df: pd.DataFrame, strict=True
    ) -> None:
        group_name = self._event_group_names[item]
        group: h5py.Group = self._handle[group_name]

        if name in group:
            del group[name]

        if strict or df is not None:
            group.create_dataset(name, data=utils.struct_from_df(df))

    def set_step(self, item: int, steps: pd.DataFrame) -> None:
        if self.on_disk:
            self._set_database(item, self._steps_database_name, steps)
        else:
            self._steps[item] = steps

    def get_step(self, item: int):
        if self.on_disk:
            return self._get_database(item, self._steps_database_name)
        else:
            return self._steps[item]

    @property
    def data(self):
        if self.on_disk:
            return self._get_database_from_all_groups(self._raw_database_name)
        else:
            return self._data

    @data.setter
    def data(self, data: list[pd.DataFrame]):
        if len(data) != len(self):
            raise ValueError(
                "Length of new data does not match number of events in object."
            )
        if self.on_disk:
            self._set_database_for_all_groups(self._raw_database_name, data)
        else:
            self._data = data

    def has_steps(self) -> list[bool]:
        if self.on_disk:
            return [
                self._steps_database_name in self._handle[group]
                for group in self._event_group_names
            ]
        else:
            return [steps_df is not None for steps_df in self._steps]

    @property
    def steps(self):
        if not any(self.has_steps()):
            return [None] * len(self)
        if self.on_disk:
            return self._get_database_from_all_groups(
                self._steps_database_name, strict=False
            )
        else:
            return self._steps

    @data.setter
    def data(self, data: list[pd.DataFrame]):
        if len(data) != len(self):
            raise ValueError(
                "Length of new data does not match number of events in object."
            )
        if self.on_disk:
            self._set_database_for_all_groups(self._raw_database_name, data)
        else:
            self._data = data

    @classmethod
    def from_raw(
        cls,
        raw: base.Raw = None,
        ios_range: tuple = (220, 250),
        n_components_current: int = 3,
        ios_extent: float = 0.999,
        known_good_voltage: tuple = None,
        n_components_voltage: int = 3,
        ignore_voltage: bool = False,
        boundary_trim: int = 5,
        resample_to_freq: float = 5000,
        max_samples: int = 1000000,
        lowpass: float = None,
        strict: bool = True,
        verbose=False,
        on_disk=False,
    ):
        """Find events in raw data.

        Applies event detection to find events in raw data.

        Args:

            raw (base.Raw): base.Raw object.
            ios_range (tuple): A tuple specifying the range in which
                the open state current lies. Units of pA. Defaults to
                (220, 250).
            n_components_current (int): Number of components for the GMM
                used to analyse the current. Defaults to 3.
            ios_extent (float): Extents of the open state
                current distribution found by the GMM that should be classified
                as indeed being open state current. Defaults to 0.999.
            known_good_voltage (:obj:`tuple`, optional): A tuple specifying the
                range in which the proper bias voltage lies. Defaults to None,
                in which case the bias voltage is found automatically. In this
                case, the bias voltage is assumed to be the distribution found
                by GMM with the largest mean. This method works well for
                constant-voltage data. For-variable voltage, GMM (naturally)
                has a hard time mapping a Gaussian distribution to the
                uniformly-distributed bias voltage sweep created by the
                triangle wave. In this case, specifying a range is necessary.
            n_components_voltage (int): Number of components for the GMM
                used to analyse the voltage. Defaults to 3.
            ignore_voltage (bool): If False, any events with irregular voltages
                are discarded. If True, voltage data is not used in event
                detection.
            boundary_trim (int): Integer specifying the amount of samples to
                trim off the end. Positive values result in trimmed ends.
                Negative values result in data around the edges of the event
                being added into the event data. Defaults to 5.
            resample_to_freq (float): A number specifying which sampling rate in Hz
                to resample the data to before running event detection.
                For measurements with a sampling rate >5 kHz (i.e.
                variable-voltage measurements), the recommended setting is 5
                kHz. Defaults to 5000. When set to None, resampling is disabled.
            max_samples (int): An integer specifying the maximum number of
                samples used for finding the open state current. If set to N,
                N/2 of the samples at the front of the data are used, along
                with N/2 of the samples at the end of the data. The data is
                split in half to account for drift in the open-state current.
            lowpass (float): A floating-point number that when set applies a
                low-pass filter with a cut-off point at that value in Hz.
                Defaults to None, for which the data is not filtered. For
                constant-voltage data, no lowpass filtering is necessary. For
                varviable-voltage measurements, it is recommended to set this
                value at half the bias voltage frequency.
            strict (bool): Boolean specifying whether to require events to be
                found. Defaults to True. When no open current within the
                specified range can be found, an error is thrown. If set to
                False, so error is raised, but an EmptyEvents is returned.
            verbose (bool): Boolean specifying whether to print progress.
             on_disk:

        Returns:
            Events: Events object containing the found events.

        """
        GOOD_RANGE_TYPES = (list, tuple, np.ndarray)
        if not isinstance(ios_range, GOOD_RANGE_TYPES):
            raise TypeError(
                "Parameter open_state_current should be a "
                "tuple specifying the range in which to search for "
                "an open state current."
            )
        if known_good_voltage and not isinstance(known_good_voltage, GOOD_RANGE_TYPES):
            raise TypeError(
                "Parameter known_good_voltage should be a "
                "tuple specifying the range of the bias votlage."
            )

        info = raw.info

        if verbose:
            print("Finding open pore current distribution... ", end="")

        try:
            eventdetection.find_open_state(
                raw,
                lower_bound=min(ios_range),
                upper_bound=max(ios_range),
                lowpass=lowpass,
                n_components=n_components_current,
                extent=ios_extent,
                resample_to_freq=resample_to_freq,
                max_samples=max_samples,
                verbose=verbose,
            )
        except eventdetection.OpenStateNotFoundError as e:
            if strict:
                raise eventdetection.EventDetectionFailure(
                    "Cannot find any events. Please check settings. If "
                    "finding no events is acceptable, i.e. in a multi-channel "
                    "or multi-acquisition setting, set strict=False."
                ) from e
            else:
                return None

        if verbose:
            print("Done!")
            print("Finding erroneous voltages... ", end="")

        if not ignore_voltage:
            eventdetection.find_bad_voltages(
                raw,
                ignore_range=known_good_voltage,
                n_components=n_components_voltage,
                resample_to_freq=resample_to_freq,
                max_samples=max_samples,
                verbose=verbose,
            )

        if verbose:
            print("Done!")
            print("Creating events... ", end="")

        properties = eventdetection.get_events_idxs(raw, boundary_trim=boundary_trim)
        add_event_time(properties, raw.info.sfreq)

        ios_fit = eventdetection.get_open_pore_fit(raw)
        ios_arr = ios_fit(raw.get_t())

        # Add metadata
        raw.info.ios = np.mean(ios_arr)

        # Create iterator
        data, ios = data_generator(raw, properties, ios_arr)

        # Let the initializer handle the creation of each database
        c = cls(
            data,
            info,
            properties,
            nums=np.arange(len(data)),
            ioss=ios,
            channels=[raw.channel] * len(data),
            start_idxs=properties["start_idx"].to_numpy(),
            on_disk=on_disk,
        )

        return c

    def find_steps(
        self,
        n_jobs=1,
        silent=False,
        **kwargs,
    ):

        if n_jobs != 1:
            manager = ParallelStepFinder(n_jobs=n_jobs, silent=silent)
            manager.start(self, **kwargs)
        else:
            for i, event in tqdm.tqdm(enumerate(self), desc="Finding steps", disable=silent):
                event.find_steps(**kwargs)

                self.set_step(i, event.steps)

            return None

    def reassign_event_numbers(self, offset: int = 0):
        self.nums = np.arange(len(self)) + offset

    def get_time(self, num):
        return self[num].get_time()

    def get_label_stats(self, label_df: pd.DataFrame = None) -> pd.DataFrame:
        labels = self.labels
        if label_df is not None:
            u_labels = label_df.label.to_numpy()
        else:
            u_labels = np.unique(labels).astype(int)

        nums = np.array([np.sum(labels == i) for i in u_labels])
        perc = nums / len(self) * 100
        df = pd.DataFrame(
            [
                u_labels,
                nums,
                perc,
            ],
            index=["Labels", "No.", "%"],
            columns=label_df.description if label_df is not None else None,
        ).astype(int)
        return df

    def _check_indexing(self, num):
        if not isinstance(num, (int, np.integer)):
            raise TypeError("Must request event with integer index.")
        elif num < 0 or num >= len(self):
            raise IndexError(
                f"Expected an event index between 0 and "
                f"{len(self) - 1}, but got {num}."
            )

    @classmethod
    def from_h5(
        cls, fname: typing.Union[os.PathLike, str], to_memory=True, strict=True
    ):
        fname = pathlib.Path(fname)

        handle = h5py.File(fname.as_posix(), "r+")
        info = base.Info.from_handle(handle)  # Read info

        data = [
            pd.DataFrame(
                index=[0], columns=[base.CURRENT_FIELD_NAME, base.VOLTAGE_FIELD_NAME]
            )
        ]
        properties = pd.DataFrame(index=[0], columns=["start_idx", "stop_idx"])

        new = cls(data, info, properties, on_disk=False)

        new._erase_memory()  # Clear data

        new._handle = handle
        new.on_disk = fname
        new._event_group_names = new._get_group_names()

        if to_memory:
            new.to_memory()

        return new

    def to_memory(self):
        if self.on_disk:
            self.info.to_memory()

            self._data = self.data
            self._steps = self.steps
            self._properties = self.properties

            # Convert proxy to list
            self._nums = list(self.nums)
            self._labels = list(self.labels)
            self._ioss = list(self.ioss)
            self._channels = list(self.channels)
            self._start_idxs = list(self.start_idxs)

            self._handle.close()
            self._handle = None
            self.on_disk = False

    def copy(self, keep_disk=False):
        """

        If on disk, will load to memory on default.

        Args:
            keep_disk:

        Returns:

        """
        if self.on_disk and keep_disk:
            fname = "copy_" + self.on_disk.name
            self.save(self.on_disk.parent / fname)
            return self
        elif self.on_disk:
            self.to_memory()
            return self
        else:
            return copy.deepcopy(self)

    def filter_by_mask(self, good_idxs, inplace=True, keep_disk=False):
        good_idxs = np.array(good_idxs, dtype=bool)
        if inplace:
            eves = self
        else:
            eves = self.copy(keep_disk)

        if eves.on_disk:
            for good, group_name in zip(good_idxs, self._event_group_names):
                if not good:
                    del eves._handle[group_name]
            eves._event_group_names = filter_list_by_mask(
                eves._event_group_names, good_idxs
            )

            # Recreate properties
            properties = eves.properties.iloc[good_idxs, :]
            del eves._handle[eves._properties_database_name]
            eves._handle.create_dataset(
                eves._properties_database_name, data=utils.struct_from_df(properties)
            )
        else:
            # Filter dataframe
            eves._properties = eves._properties.iloc[good_idxs, :]
            eves._properties.reset_index(inplace=True, drop=True)

            # Filter arrays
            eves._data = filter_list_by_mask(eves._data, good_idxs)
            eves._steps = filter_list_by_mask(eves._steps, good_idxs)
            eves._nums = filter_list_by_mask(eves._nums, good_idxs)
            eves._labels = filter_list_by_mask(eves._labels, good_idxs)
            eves._ioss = filter_list_by_mask(eves._ioss, good_idxs)
            eves._channels = filter_list_by_mask(eves._channels, good_idxs)
            eves._start_idxs = filter_list_by_mask(eves._start_idxs, good_idxs)

            # Change event number attributes
            eves.reassign_event_numbers()

        return eves

    def filter_by_labels(self, include=None, exclude=None, **kwargs):
        labels = np.array(self.labels)

        if include is None and exclude is None:
            raise ValueError("Please specify which labels to include or " "exclude.")
        elif include is not None and exclude is not None:
            raise ValueError("Please specify either include or exclude.")
        elif isinstance(include, (int, np.integer)):
            include = [include]
        elif isinstance(exclude, (int, np.integer)):
            exclude = [exclude]

        if exclude is not None:
            include = np.unique(labels)
            include = np.setdiff1d(include, exclude)

        mask = np.isin(labels, include)
        return self.filter_by_mask(mask, **kwargs)

    def filter_by_step_rate(self, r: float = 10, strict: bool = True, **kwargs):
        """

        Args:
            r (float): Minimum step rate for inclusion in Hz. Average Hel308 step rate is 20 Hz `(Noakes 2019)`_., so defaults to 10 Hz.
            strict:
            **kwargs:

        Returns:



        .. _(Noakes 2019): https://www.nature.com/articles/s41587-019-0096-0
        """
        step_rates = np.zeros(len(self))

        sfreq = self.info.sfreq

        for i, eve in enumerate(self):
            steps = eve.steps
            if strict and steps is None:
                raise ValueError(
                    f"Event {eve.num} does not have any steps. Please run "
                    f"change point detection."
                )
            elif steps is None:
                steps = 0  # Always excluded
            else:
                steps = len(eve.steps)

            step_rates[i] = steps / len(eve) * sfreq

        return self.filter_by_mask(step_rates > r, **kwargs)

    def filter_by_event_length(
        self, min_duration: float = 0.1, verbose=False, **kwargs
    ):

        if "dur_s" not in self.properties.columns:
            raise KeyError(
                "No key 'dur_s' found in event properties "
                "dataframe. Try running Events.add_event_time "
                "first."
            )

        good_idxs = self.properties["dur_s"] >= min_duration

        if verbose:
            print(
                f"Found {sum(good_idxs)} events from {len(good_idxs)} with "
                f"a duration of {min_duration} seconds or longer."
            )

        return self.filter_by_mask(good_idxs, **kwargs)

    def filter_by_current_range(
        self,
        current_range: tuple = (0.15, 0.75),
        threshold: float = 0.9,
        verbose=False,
        strict: bool = True,
        **kwargs,
    ):
        """Filters by comparing event current to open pore current.

        Gets the open pore current and determines the number of samples of that
        event that lie within a range determined relative to the open pore
        current. If the fraction of points within the range is above a
        threshold, the event is kept.

        TODO: Update docstring

        Args:
            current_range (tuple): Tuple containing two values that set the
                range relative to the open pore current. For example, if the
                open pore current is 300 pA, `current_range=(0.333, 0.666)`
                would result in a range from 100 to 200 pA. Defaults to
                (0.25, 0.75).
            threshold (float): A float specifying the minimum fraction of
                samples which have to lie in the correct range for an event to
                be kept. Defaults to 0.9.
            verbose (bool): Whether to print information on the number of
                kept events.
            strict (bool): Whether to raise an exception if any of the events
                have no information on the open pore current. If set to False,
                the method works even for any events do not have open pore
                current. Such events are then kept. Defaults to True.
        """
        good_idxs = np.ones(len(self), dtype=bool)
        for i, event in enumerate(self):
            if event.ios is None:
                if strict:
                    raise ValueError(
                        f"Event {i} has not been " f"assigned an open pore current."
                    )
                else:
                    continue

            upper_bound = event.ios * max(current_range)
            lower_bound = event.ios * min(current_range)

            in_range = (event.i > lower_bound) & (event.i < upper_bound)

            if np.sum(in_range) / len(event) < threshold:
                good_idxs[i] = False

        if verbose:
            print(
                f"Found {sum(good_idxs)} events from {len(good_idxs)} with "
                f"at least {threshold:.0%} of samples within a range of "
                f"{min(current_range):.0%}-{max(current_range):.0%} of the "
                f"open pore current."
            )

        return self.filter_by_mask(good_idxs, **kwargs)

    def view(self, labels: dict = None):
        """Interactive viewer.

        Creates widget for viewing and labeling events. Requires `ipyml` and
        `ipywidgets`. Can also add colors and labels.

        See Also:
            varv.utils.eventviewer.EventViewer
            varv.utils.eventviewer.Label

        Args:
            labels:

        Returns:

        """
        from varv import widgets

        return widgets.EventViewer(self, labels)()


class EmptyEvents(Events):

    def __init__(self):
        data = [
            pd.DataFrame(
                index=[0], columns=[base.CURRENT_FIELD_NAME, base.VOLTAGE_FIELD_NAME]
            )
        ]
        properties = pd.DataFrame(index=[0], columns=["start_idx", "stop_idx"])
        super().__init__(data, base.EmptyInfo(), properties)

    def filter_by_event_length(self, *ags):
        pass

    def filter_by_current_range(self, *args):
        pass


def _worker(qin: mp.Queue, qout: mp.Queue) -> None:

    while True:
        task = qin.get(timeout=100)

        if task:
            j, sfreq, period, i, v, kwargs = task

            if period:  # Variable voltage data
                steps = changepoint.get_step_df(i, v, sfreq, period, **kwargs)
            else:
                steps = changepoint_cv.get_step_df(i, sfreq, **kwargs)

            qout.put((j, steps))
        else:
            return


class ParallelStepFinder:

    def __init__(
        self,
        n_jobs=-1,
        silent=False,
    ):
        if n_jobs < 0:
            n_jobs = mp.cpu_count() + 1 + n_jobs
        elif n_jobs == 0:
            n_jobs = 0

        self.n_jobs = n_jobs
        self.pbar = None
        self.silent = silent

    def start(self, eves: Events, **kwargs):

        if len(eves) == 0:
            return

        qin = mp.Queue(maxsize=self.n_jobs)
        qout = mp.Queue(maxsize=self.n_jobs)

        n = len(eves)

        pbar = tqdm.tqdm(total=n, desc=f"Finding steps using {self.n_jobs} processes", disable=self.silent)

        processes = []
        # Create processes
        for sent in range(self.n_jobs):
            p = mp.Process(
                target=_worker,
                args=(
                    qin,
                    qout,
                ),
            )
            p.start()
            processes.append(p)

        # Assign tasks
        sent = 0
        retrieved = 0
        while True:
            if sent < len(eves):
                eve = eves[sent]
                if eve.is_varv():
                    task = [
                        sent,
                        eve.info.sfreq,
                        eve.get_bv_period(),
                        eve.i,
                        eve.v,
                        kwargs,
                    ]
                else:
                    task = [sent, eve.info.sfreq, None, eve.i, None, kwargs]

                # Start a task if space in queue
                qin.put(task, block=True)
                sent += 1

            # Store the result of a task when a task is done
            try:
                k, df = qout.get(block=False)
            except queue.Empty:
                continue
            eves.set_step(k, df)
            retrieved += 1
            pbar.update(1)

            if retrieved == len(eves):
                break

        # Send done signal
        for sent in range(self.n_jobs):
            qin.put([])

        # Wait for processes to end and close
        [p.join() for p in processes]
        [p.close() for p in processes]
        qin.close()
        qout.close()

        pbar.close()
