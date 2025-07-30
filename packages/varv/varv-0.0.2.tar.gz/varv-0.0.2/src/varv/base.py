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
#
import copy
import os
import pathlib
import typing

import h5py
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from varv import utils, config

DATA_GROUP_NAE = "Data"

# HDF constants
VOLTAGE_FIELD_NAME = "v"
CURRENT_FIELD_NAME = "i"
CONDUCTANCE_FIELD_NAME = "g"
STATE_FIELD_NAME = "state"

# Plotting constants
Y_LABELS = {"v": "$V$ (mV)", "i": "$I$ (pA)"}

# States constants
UNLABELED_STATE = -1
GOOD_STATE = 0
OPEN_STATE = 1
BAD_VOLTAGE_STATE = 2
STATES = {
    UNLABELED_STATE: "Unlabeled",
    GOOD_STATE: "Good",
    BAD_VOLTAGE_STATE: "Bad Voltage",
    OPEN_STATE: "Open",
}

START_IDX_ATTR_NAME = "start_idx"
CHANNEL_ATTR_NAME = "channel"


class VirtualHDFGroup:

    def __init__(self, d: dict = None):
        self.attrs = d if d is not None else {}


def info_write_attr(handle, key, value):
    if value is not None:
        handle["Info"].attrs[key] = value


class Info:
    """Metadata from nanopore measurements.

    This class encapsulates information about a nanopore experiment. It stores sampling rate, the channel used, start
    index, information on the bias voltage, and other metadata. It also provides methods to manipulate, retrieve,
    store that data.

    Attributes:
        sfreq (float): Sampling frequency of the data in Hz.
        name (str): Name or identifier associated with the dataset.
        start_idx (int): Index where the data starts.
        channel (int): Channel number associated with the data.
        label (int): Label associated with the data.
        bdc (float): DC bias voltage in pA.
        bamp (float, optional): Amplitude of the bias voltage in pA.
        bfreq (float, optional): Frequency of the bias voltage in Hz.
        ios (float, optional): Measurement of open channel current in pA.
        handle (h5py.File or dict): Internal handle for storing and retrieving HDF5 group or
                                    virtual metadata structure.

    Notes:
        Upon creation it reads and writes into a virtual `HDF`_  file.
        Using :py:meth:`~varv.base.Info.set_handle`

    .. _HDF: https://www.hdfgroup.org/
    """

    def __init__(
        self,
        sfreq: float,
        name: str = None,
        bdc: float = 0,
        bamp: float = None,
        bfreq: float = None,
        ios=None,
        handle: h5py.File = None,
    ):
        # Virtual handle instead of file.
        if handle is None:
            self._handle = {
                "Info": VirtualHDFGroup(
                    {
                        "sfreq": sfreq,
                        "name": name,
                        "bcd": bdc,
                        "bamp": bamp,
                        "bfreq": bfreq,
                        "ios": ios,
                    }
                )
            }
        else:
            self._handle = handle

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.sfreq == other.sfreq
            and self.bdc == other.bdc
            and self.bamp == other.bamp
            and self.bfreq == other.bfreq
            and self.ios == other.ios
        )

    def __str__(self):
        return self.as_dataframe().__str__()

    def __repr__(self):
        table = {k: str(v) for k, v in self.as_dict().items()}
        table["on_disk"] = str(self.on_disk)
        message = " ".join([f"{k}=" + "{" + k + "}," for k in table.keys()])
        return f"{self.__class__.__name__}({message.format(**table)})"

    @property
    def bamp(self):
        return self._get("bamp")

    @bamp.setter
    def bamp(self, value):
        self._set("bamp", value)

    @property
    def bfreq(self):
        return self._get("bfreq")

    @bfreq.setter
    def bfreq(self, value):
        self._set("bfreq", value)

    @property
    def bdc(self):
        return self._get("bcd")

    @bdc.setter
    def bdc(self, value):
        self._set("bcd", value)

    @property
    def ios(self):
        return self._get("ios")

    @ios.setter
    def ios(self, value):
        self._set("ios", value)

    @property
    def name(self):
        return self._get("name")

    @name.setter
    def name(self, value):
        self._set("name", value)

    @property
    def sfreq(self):
        return self._get("sfreq")

    @sfreq.setter
    def sfreq(self, value):
        self._set("sfreq", value)

    def _set(self, key, value):
        info_write_attr(self._handle, key, value)

    def _get(self, key):
        if key in self._handle["Info"].attrs:
            return self._handle["Info"].attrs[key]
        else:
            return None

    def as_dict(self):
        return {k: v for k, v in self._handle["Info"].attrs.items()}

    def as_dataframe(self):
        """Converts the metadata into a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing metadata.
            values.
        """
        df = pd.DataFrame(
            {
                "": [
                    self.name,
                    f"{self.sfreq:.2f} Hz",
                    f"{self.bdc:.2f} mV",
                    f"{self.bamp:.2f} mV" if self.bamp else str(None),
                    f"{self.bfreq:.2f} Hz" if self.bfreq else str(None),
                    f"{self.ios:.2f} pA" if self.ios else str(None),
                ]
            }
        )
        df.index = [
            "Name",
            "Sampling Rate",
            "Bias Voltage DC",
            "Bias Voltage Amplitude",
            "Bias Voltage Frequency",
            "Open Channel Current",
        ]
        return df

    @classmethod
    def from_handle(cls, handle: h5py.File):
        return cls(0, handle=handle)

    def set_handle(self, handle: h5py.File):
        self._handle = handle

    def set_and_write_handle(self, handle: h5py.File | dict):
        """
        Sets the `handle` attribute to the specified HDF5 file handle and ensures that
        the required 'Info' group exists within it. Attributes from the current 'Info'
        group are transferred to the new handle. This allows for maintaining relevant
        metadata when switching the handle.

        Args:
            handle (h5py.File): The new HDF5 file handle to be set. If the 'Info' group
                is missing in this handle, it will be created.
        """
        meta = self._handle["Info"]

        if "Info" not in handle:
            handle.create_group("Info")

        # Copy over all attributes to the new handle
        for key, value in meta.attrs.items():
            info_write_attr(handle, key, value)

        # Set new handle
        self._handle = handle

    def to_memory(self):
        handle = {"Info": VirtualHDFGroup({})}
        self.set_and_write_handle(handle)

    def copy(self):
        """Creates a copy in memory.

        Regardless if original is on disk or not.

        Returns:

        """
        old_handle = self._handle
        self.to_memory()
        new = copy.deepcopy(self)
        self._handle = old_handle
        return new

    @property
    def on_disk(self):
        return not isinstance(self._handle, dict)


class BaseData:
    _fname_format = "{}.h5"
    _raw_database_name = "Raw"
    _info_group_name = "Info"

    def __init__(self, info, on_disk: bool | str | pathlib.Path = False):
        self.info: Info = info
        self._data = None
        self._handle = None  # File for storing data
        self.on_disk = False  # Init on memoryte
        self._raw_path = None

        self._set_disk(on_disk)

    def __repr__(self):
        table = {k: str(v) for k, v in self.info.as_dict().items()}
        table["on_disk"] = str(bool(self.on_disk))
        message = " ".join([f"{k}=" + "{" + k + "}," for k in table.keys()])
        return f"{self.__class__.__name__}({message.format(**table)})"

    def _set_disk(self, on_disk):
        # Find out whether to save on disk or keep in memory
        if on_disk is True:
            # Save on disk. Auto generate name
            self.on_disk = self._get_save_fname()
        elif on_disk is not False:
            # Save on disk with given filename.
            on_disk = pathlib.Path(on_disk)
            if on_disk.is_dir():
                on_disk = on_disk / self._get_save_fname()
            self.on_disk = on_disk.with_suffix(".h5")
        else:
            # Load in memory
            self.on_disk = False

    def _set_data_group_name(self, name: str):
        self._data_group_name = name
        self._raw_path = f"/{name}/{self._raw_database_name}"

    def __del__(self):
        if self._handle is not None:
            self._handle.close()

    def __eq__(self, other):
        return self.info == other.info

    def _copy_to_new_file(self, fname):
        raise NotImplementedError()

    def _erase_memory(self):
        raise NotImplementedError()

    def _get_save_fname(self):
        return self._fname_format.format(self.info.name)

    @classmethod
    def _init_dummy(cls, info):
        raise NotImplementedError()

    def _save_from_memory_to_file(self, fname):
        self._handle = h5py.File(fname, "w")
        self._handle.create_group(self._data_group_name)
        self.info.set_and_write_handle(self._handle)

    @classmethod
    def from_h5(
        cls, fname: typing.Union[os.PathLike, str], to_memory=True, strict=True
    ):
        fname = pathlib.Path(fname)

        handle = h5py.File(fname.as_posix(), "r+")

        info = Info.from_handle(handle)  # Read info

        new = cls._init_dummy(info)

        if strict and new._data_group_name not in handle:
            raise TypeError(
                f"Error, tried to create new {type(new).__name__} from file, but only found "
                f'{", ".join(handle.keys())} types in file.'
            )

        new._erase_memory()  # Clear data

        new._handle = handle
        new.on_disk = fname

        if to_memory:
            new.to_memory()

        return new

    def save(self, fname: typing.Optional[os.PathLike] = None, dump=False):
        """

        Args:
            fname (str): File name to save to. If no filename is provided, one
              is created using name information.
            dump (bool): Whether to dump data in memory to disk or not. If set
              to True, erases data in memory after saving the file and data
              on disk is used. If set to False, writes data to disk but keeps
              references to the data in memory.

        Returns:


        """
        if self.on_disk and fname is None:
            return  # Already on disk, do nothing.

        if fname is None:
            fname = self._get_save_fname()
        fname = pathlib.Path(fname)

        if fname.is_dir():  # fname is folder to save to
            fname = fname / self._get_save_fname()

        fname = pathlib.Path(fname).with_suffix(".h5")

        if self.on_disk and fname != self.on_disk:
            # Data on disk already, just copy to new file.
            self._copy_to_new_file(fname)
        elif not self.on_disk:
            # If in memory, create file and use for storage.
            self._save_from_memory_to_file(fname)

            if dump:
                self._erase_memory()  # Reset data, using handle now
                self.on_disk = fname
            else:
                # Back to memory
                self.info.to_memory()
                self._handle.close()
                self._handle = None
        else:
            # Already loaded on disk and with same filename, so do not change
            # anything
            pass

    def to_disk(self, fname: typing.Optional[os.PathLike | str] = None) -> None:
        self.save(fname=fname, dump=True)

    def to_memory(self):
        if self.on_disk:
            self.info.to_memory()

            raise NotImplementedError()

    def _get_attr(self, name, on_disk: bool = None, strict=False):
        on_disk = self.on_disk if on_disk is None else self.on_disk
        if on_disk:
            attrs = self._handle[self._data_group_name].attrs
            if name in attrs:
                return attrs[name]
            elif strict:
                raise AttributeError("Could not find attribute on disk.")
            else:
                return None
        else:
            return getattr(self, self._get_memory_attr_name(name))

    def _set_attr(self, name, value, on_disk: bool = None, strict=False):
        on_disk = self.on_disk if on_disk is None else on_disk
        if not on_disk:
            setattr(self, self._get_memory_attr_name(name), value)
        elif strict and value is None:
            raise ValueError(
                "Attribute value cannot be None. Either change or change "
                "strictness of setter."
            )
        elif value is not None:
            self._handle[self._data_group_name].attrs[name] = value

            pass

    def _write_attrs(self, **kwargs):
        assert self._data_group_name in self._handle

        for name, value in kwargs.items():
            self._set_attr(name, value, on_disk=True)

    def _write_databases(self, **kwargs) -> None:
        for name, data in kwargs.items():
            self._handle[self._data_group_name].create_dataset(
                name, data=utils.struct_from_df(data)
            )

    @staticmethod
    def _get_memory_attr_name(name):
        return f"_{name}"


class Data(BaseData):

    def __init__(
        self,
        info: Info,
        data: pd.DataFrame,
        on_disk: bool | str | pathlib.Path = False,
        channel: int = None,
        start_idx: int = None,
        **kwargs,
    ):
        """

        Args:
            info:
            data:
            channel:
            start_idx:
            on_disk:
        """
        assert CURRENT_FIELD_NAME in data.columns
        assert VOLTAGE_FIELD_NAME in data.columns

        super().__init__(info, on_disk)

        self._channel = channel
        self._start_idx = start_idx
        self._data = data

        self._set_data_group_name("Data")

        if on_disk:
            self._save_from_memory_to_file(self.on_disk)
            self._erase_memory()

    def __eq__(self, other):
        return (
            self.info == other.info
            and self.data.equals(other.data)
            and self.channel == other.channel
            and self.start_idx == other.start_idx
        )

    def __getitem__(self, item):
        field, idx, _ = self._check_field_and_indices(item)

        if self.on_disk and field is None:
            arr = self._handle[self._raw_path][idx]
            return utils.df_from_struct(arr)
        elif self.on_disk:
            return self._handle[self._raw_path].fields(field)[idx]
        elif field:
            field_idx = self._data.columns.get_loc(field)
            return self._data.iloc[idx, field_idx].to_numpy()
        else:
            return self._data.iloc[idx]

    def __len__(self):
        if self.on_disk:
            return self._handle[self._raw_path].shape[0]
        else:
            return len(self.data.index)

    def __repr__(self):
        table = self.info.as_dict()
        table["on_disk"] = bool(self.on_disk)
        table["channel"] = self.channel
        table["start_idx"] = self.start_idx
        table = {k: str(v) for k, v in table.items() if v is not None}
        message = " ".join([f"{k}=" + "{" + k + "}," for k in table.keys()])
        return f"{self.__class__.__name__}({message.format(**table)})"

    def __str__(self):
        df = self.info.as_dataframe()
        df_dur = pd.DataFrame(
            [
                [f"{self.duration:.2f} s"],
                [f"{len(self)}"],
                [f"{self.channel}"],
                [f"{self.start_idx}"],
            ],
            columns=[""],
        )
        df_dur.index = ["Duration", "No. Samples", "Channel", "Start Index"]
        df = pd.concat([df, df_dur])
        return df.__str__()

    def __setitem__(self, key, value):
        field, idx, key = self._check_field_and_indices(key)

        new = (not self.has_field(field)) if field is not None else False

        if new:
            try:
                n = len(value)
            except TypeError:
                n = None

            if n is not None and len(value) != len(self):
                raise ValueError(
                    f'Length of new field "{field}" ({len(value)}) is not '
                    f"equal to length of data ({len(self)})."
                )

        if self.on_disk:
            if new:
                arr = self._handle[self._raw_path][()]
                new_arr = utils.add_field_to_struct(arr, field)
                del self._handle[
                    f"/{self._data_group_name}" f"/{self._raw_database_name}"
                ]
                self._handle[self._data_group_name].create_dataset(
                    self._raw_database_name, data=new_arr
                )

            self._handle[self._raw_path][key] = value
        elif new:
            self._data[field] = value
        elif field:
            field_idx = self._data.columns.get_loc(field)
            self._data.iloc[idx, field_idx] = value
        else:
            self._data.iloc[idx] = value

    @property
    def channel(self):
        return self._get_attr(CHANNEL_ATTR_NAME)

    @channel.setter
    def channel(self, value):
        self._set_attr(CHANNEL_ATTR_NAME, value)

    @property
    def data(self) -> pd.DataFrame:
        # TODO: Make this like event.steps
        if self.on_disk:
            arr = self._handle[self._raw_path][()]
            return utils.df_from_struct(arr)
        else:
            return self._data

    @data.setter
    def data(self, df: pd.DataFrame):
        assert CURRENT_FIELD_NAME in df.columns
        assert VOLTAGE_FIELD_NAME in df.columns
        if self.on_disk:
            self._handle[self._raw_path] = utils.struct_from_df(df)
        else:
            self._data = df

    @property
    def duration(self):
        return len(self) / self.info.sfreq

    @property
    def i(self):
        """

        Returns:

        Notes:
            If using on-disk data, this returns the data as a copied numpy
            array. Changes to this array will not affect the data. Instead,
            change data by slicing directly.

            Don't:
                bd = BaseData()
                bd.i[:10] = 0
            Do:
                bd['i', :10] = 0

        """
        return self[CURRENT_FIELD_NAME]

    @i.setter
    def i(self, value):
        self[CURRENT_FIELD_NAME] = value

    @property
    def start_idx(self):
        return self._get_attr(START_IDX_ATTR_NAME)

    @start_idx.setter
    def start_idx(self, value):
        self._set_attr(START_IDX_ATTR_NAME, value)

    @property
    def v(self):
        return self[VOLTAGE_FIELD_NAME]

    @v.setter
    def v(self, value):
        self[VOLTAGE_FIELD_NAME] = value

    def _check_field_and_indices(self, key):
        IDX_TYPES = (slice, int, list, np.ndarray)
        idx = slice(None)
        field = None
        if isinstance(key, tuple):
            if (
                len(key) != 2
                or not isinstance(key[0], str)
                or not isinstance(key[1], IDX_TYPES)
            ):
                raise IndexError(
                    f"Expected double index to be first a field "
                    f"name followed by an index, slice, or mask but got"
                    f"{key}"
                )
            field = key[0]
            idx = self._check_indices(key[1])
            new_key = (field, idx)
        elif isinstance(key, str):
            field = key
            new_key = field
        elif isinstance(key, IDX_TYPES):
            idx = self._check_indices(key)
            new_key = idx
        else:
            raise IndexError(
                "Invalid slicing. Please use either a field name as "
                "a string, or a slice of indices, a list of indices, "
                "a boolean mask or both."
            )

        return field, idx, new_key

    def _check_indices(self, idxs):
        if isinstance(idxs, (slice, int)):
            return idxs
        elif isinstance(idxs, (list, np.ndarray)):
            # Either a list of indexes of boolean mask
            is_mask = len(idxs) == len(self) and self.on_disk
            if is_mask:
                return [i for i, included in enumerate(idxs) if included]
            else:
                return idxs
        else:
            raise IndexError(
                f"Expected indexing to be either a single index, a list "
                f"of indices, or a boolean mask of length equal to the data, "
                f"but got {type(idxs)} index {idxs} of length {len(idxs)}"
            )

    def _copy_to_new_file(self, fname):
        with h5py.File(fname, "w") as handle_dest:
            self._handle.copy(
                self._handle[self._data_group_name], handle_dest, self._data_group_name
            )
            self._handle.copy(
                self._handle[self._info_group_name], handle_dest, self._info_group_name
            )

    def _erase_memory(self):
        self._data = None
        self._label = None
        self._channel = None
        self._start_idx = None

    @classmethod
    def _init_dummy(cls, info: Info):
        # Dummy data
        data = pd.DataFrame(index=[0], columns=[CURRENT_FIELD_NAME, VOLTAGE_FIELD_NAME])
        new = cls(info, data, on_disk=False)
        return new

    def _save_from_memory_to_file(self, fname):
        super()._save_from_memory_to_file(fname)

        attrs = {
            CHANNEL_ATTR_NAME: self._channel,
            START_IDX_ATTR_NAME: self._start_idx,
        }
        self._write_attrs(**attrs)
        databases = {self._raw_database_name: self._data}
        self._write_databases(**databases)

    def get_nyquist(self):
        return self.info.sfreq / 2

    def get_t(self, start=None, stop=None, as_ms=False):
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        t = np.arange(start, stop) / self.info.sfreq
        if as_ms:
            t *= 1e3
        return t

    def get_time(self, **kwargs):
        return self.get_t(**kwargs)

    def has_conductance(self):
        return self.has_field(CONDUCTANCE_FIELD_NAME)

    def has_field(self, field) -> bool:
        if self.on_disk:
            return field in self._handle[self._raw_path].dtype.fields.keys()
        else:
            return field in self.data

    def is_varv(self):
        return (
            self.info.bfreq is not None
            and self.info.bfreq > 0
            and self.info.bamp is not None
            and self.info.bamp > 0
        )

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
        **kwargs,
    ):

        ax, field, fig, start, stop = self._plot_init(field, start, stop, fig, ax)

        x = self.get_time()[start:stop]
        y = self[field, start:stop]

        if lowpass:
            y = utils.lowpass_filter(y, self.info.sfreq, lowpass)

        ax.plot(x, y, fmt, **kwargs)

        ax.set_xlabel("$t$ (s)", fontsize=14)
        ax.set_ylabel(Y_LABELS[field], fontsize=14)

        ax.set_title(self.info.name + "\nData")

        self._end_plot(fig, savefig)

        return fig, ax

    def _end_plot(self, fig, savefig):
        if savefig:
            fig.savefig(savefig, dpi=300)
        fig.tight_layout()

    def _plot_init(self, field, start, stop, fig, ax):
        if fig is None and ax is None:
            fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE, dpi=150)
        if fig is None or ax is None:
            raise ValueError("Need to pass a figure or axes argument or neither. ")
        field = field.lower()
        if field not in [CURRENT_FIELD_NAME, VOLTAGE_FIELD_NAME]:
            raise ValueError(
                'Please set variable to plot "var" to '
                'either "i" for current or "v" for voltage.'
            )
        get_idx = lambda t: (
            int(np.clip(t * self.info.sfreq, 0, len(self))) if t else None
        )
        start = get_idx(start)
        stop = get_idx(stop)
        return ax, field, fig, start, stop

    def reset_indices(self):
        """Resets indices of data"""
        self.info.start_idx = self.data.index[0]
        self.data.reset_index(inplace=True, drop=True)

    def to_memory(self):
        if self.on_disk:
            self.info.to_memory()

            self._data = self.data
            self._start_idx = self.start_idx
            self._channel = self.channel
            self._handle.close()
            self._handle = None
            self.on_disk = False

    def truncate(self, before=None, after=None, inplace=True):
        if not self.on_disk and inplace:
            self.data = self.data.truncate(before=before, after=after)
        elif not self.on_disk:
            new_obj = copy.deepcopy(self)
            new_obj.truncate(before=before, after=after)
            return new_obj
        elif self.on_disk and inplace:
            df = self.data.truncate(before=before, after=after)
            del self._handle[self._raw_path]

            self._handle[self._data_group_name].create_dataset(
                self._raw_database_name, data=utils.struct_from_df(df)
            )
        else:
            raise ValueError("Can only truncate on disk if inplace is True.")


class Raw(Data):
    _fname_format = "{}_raw.h5"

    def __init__(
        self,
        info: Info,
        data: pd.DataFrame,
        on_disk: bool | str | pathlib.Path = False,
        channel: int = None,
        start_idx: int = None,
        **kwargs,
    ):
        """

        Args:
            info:
            data:
            channel:
            start_idx:
            on_disk:
        """
        super().__init__(info, data, False, channel, start_idx)

        # Override group name
        self._set_data_group_name("Raw")

        # Save to disk if needed
        self._set_disk(on_disk)
        if on_disk:
            self._save_from_memory_to_file(self.on_disk)
            self._erase_memory()

    @property
    def state(self) -> np.ndarray | None:
        if self.has_field(STATE_FIELD_NAME):
            return self[STATE_FIELD_NAME]
        else:
            # raise AttributeError('No state data available.')
            return None

    @state.setter
    def state(self, states: np.ndarray = None):
        if states is None:
            states = 0
        else:
            assert len(states) == len(self), "States not same " "length as events"
        self[STATE_FIELD_NAME] = states

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
        max_points: int = 1000000,
        show_states: bool = False,
        **kwargs,
    ):
        ax, field, fig, start, stop = self._plot_init(field, start, stop, fig, ax)

        y = self[field, start:stop]

        if self.has_state():
            s = self.state[start:stop]
        else:
            s = np.zeros_like(y, dtype=bool)

        if lowpass:
            y = utils.lowpass_filter(y, self.info.sfreq, lowpass)

        if len(y) > max_points:
            y = utils.downsample_by_exact_factor(y, max_points)
            s = utils.downsample_by_exact_factor(s, max_points)

        if start is None:
            start = 0
        if stop is None:
            stop = len(self)

        x = np.linspace(start, stop, len(y)) / self.info.sfreq

        if len(x) > 1000:
            fmt = "."
            kwargs.update({"markersize": 1})

        if show_states:
            for state in np.unique(s):
                mask = s == state
                ax.plot(
                    x[mask],
                    y[mask],
                    fmt,
                    label=f"{STATES[state]}" if self.has_state() else None,
                    **kwargs,
                )
        else:
            ax.plot(x, y, fmt, **kwargs)

        ax.set_xlabel("Time (s)", fontsize=14)
        ax.set_ylabel(Y_LABELS[field], fontsize=14)

        if show_states and self.has_state():
            ax.legend(loc=3)

        if field == "i" and not self.is_varv():
            ax.set_ylim([0, 250])

        ax.set_title(self.info.name + "\nRaw")

        self._end_plot(fig, savefig)

        return fig, ax

    def has_state(self):
        return self.has_field(STATE_FIELD_NAME)

    def reset_states(self):
        self[STATE_FIELD_NAME] = GOOD_STATE


class EmptyInfo(Info):

    def __init__(self):
        super().__init__(0)
