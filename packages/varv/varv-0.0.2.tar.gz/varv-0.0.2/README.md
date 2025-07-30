# varv

[![pipeline status](https://gitlab.tudelft.nl/xiuqichen/varv/badges/main/pipeline.svg)](https://gitlab.tudelft.nl/xiuqichen/varv/-/commits/main)
 [![Latest Release](https://gitlab.tudelft.nl/xiuqichen/varv/-/badges/release.svg)](https://gitlab.tudelft.nl/xiuqichen/varv/-/releases)
![PyPI - Version](https://img.shields.io/pypi/v/varv)


Repository for the code of Thijn Hoekstra's thesis. The goal of this project is to implement variable voltage in the 
nanopore measurement of DNA-peptide conjugates. The repository contains Python modules that provides a high-level 
interface for dealing with nanopore data in general, and variable-voltage nanopore data in particular.

The documentation is currently work in progress, but HTML files can be found in the ``docs`` folder.

This code GNU general licensed.

## Description

Currently, there does not seem to be a standard for handling nanopore data. Oxford Nanopore Technologies data provides 
many [packages](https://github.com/nanoporetech) for their platform, but these do not generalise well to the data 
created by custom nanopore setups like the one used in the [Cees Dekker](https://ceesdekkerlab.nl/) lab. 

Another issue with nanopore data analysis is that many current methods use code written in MATLAB. The experience 
during this thesis has highlighted a couple disadvantages. For one, MATLAB code is generally less broadly used and 
understood. In addition, this code has been harder to maintain, document, and most importantly has issues with 
portability.

The goal of this repository is to start to address these two issues, first by porting and integrating nanopore analysis 
code in a single Python module. This module should also be easy to install and run on every computer.

This module is inspired by [MNE](https://mne.tools/1.8/development/contributing.html), which is an open-source Python 
package for managing EEG and MEG data.

## Installation

### (Extra) On virtual environments

The recommended installation method for this package is to install it via the ``pip`` package installer into a 
[virtual environment](https://docs.python.org/3/library/venv.html). For more information on virtual environments, read 
this [section](https://interactivetextbooks.tudelft.nl/programming-foundations/content/chapter7/numpy-package.html#importing-a-package) 
in *Programming Foundations*, an open-access book on Python programming foundations [[1]](#1).

If you are already familiar with creating a virtual environment, skip ahead to the next section. If you use ``conda``, 
you can skip this step and create a virtual environment using it instead. It is assumed that you 
have installed [Python](https://www.python.org/downloads/) and know how to open a terminal. To create a virtual 
environment open a terminal at a location of your choosing and run:

```shell
python -m venv .venv
```

This creates a virtual environment in which to install the Python packages. This virtual environment is stored in a 
folder called `.venv`. To activate the virtual environment, run:

```shell
source .venv/bin/activate
```

For Windows, use:

```shell
.venv\Scripts\activate.bat
```

If activated correctly, ``(.venv) `` should appear on the left of your terminal line. Next, install the ``varv`` module 
using the instructions in the next section.

### Install using PyPI
```varv``` is listed on [PyPI](https://pypi.org/project/varv/) and can be easily installed using the package manager 
``pip``, simply using:

```shell
pip install varv
```

Note that there is no ``conda`` distribution for this package yet, so also install it via ``pip`` or from source 
(described in the section below).

For extra Jupyter interactivity (not recommended).
```shell 
pip install varv[jupyter]
```

### Install from source
If you intend to develop or modify ``varv`` or try the latest version, install the package from source. Once again, 
make sure you install into a virtual environment. To install from source, first open a terminal and navigate to a 
directory of your choice, then clone the repository:

```shell
git clone https://gitlab.tudelft.nl/xiuqichen/varv.git
```

Note that this requires [Git](https://git-scm.com/). For more information on version control using Git, check out 
this [section](https://interactivetextbooks.tudelft.nl/programming-foundations/content/chapter3/git-intro.html#version-control-with-git) 
in *Programming Foundations* [[1]](#1). 

Next, move into the ``varv`` directory.

```shell
cd varv
```

Finally, install an editable version of the package. `[Dev]` [installs](https://devsjc.github.io/blog/20240627-the-complete-guide-to-pyproject-toml/#ditching-requirements-txt) the packages needed for development, 
like testing and documentation/

```shell
pip install -e '.[dev]'
```

## How to use

``varv`` provides some high-level objects for managing nanopore sequencing data. Each of the following sections 
describes a useful class for handling such data.

#### Managing measurement metadata
Consider a nanopore measurement. It involves many parameters, for example a name specifying the sample and conditions, 
a bias voltage of a certain magnitude over the membrane, or the sampling rate it was measured at. These metadata can be 
neatly stored using the Info class.

For example, to store metadata for a measurement with a sampling rate of 5 kHz, a name *Sample A*, and a (constant) 
bias voltage of 180 mV, write:

```python
from varv.base import Info

info = Info(5e3, "Sample A", 180)
```

This info can be displayed by calling ``print(info)``. More metadata can also be stored, like:
- Bias voltage amplitude (in the case of a variable voltage measurement setup)
- Bias voltage frequency (in the case of a variable voltage measurement setup)
- Open state current (in pA)


#### Managing data for experiments

To store data measured over an entire run of an experiment (typically with a duration ~1000s), use the ``Raw`` class, 
which is created using an ``Info`` object and the data as a pandas dataframe:

```python
import numpy as np
import pandas as pd

from varv.base import Raw, Info

data = pd.DataFrame(
 columns=["i", "v"], 
 data=np.random.random((100, 2)))

raw = Raw(Info(5e3), data)
print(raw)

# For multichannel data, you can specify a channel number
raw_2 = Raw(Info(5e3), data, channel=2)  
```

In the Cees Dekker lab, the nanopore data is stored as a `.dat` file created by LabView. These can be converted to a 
raw object:

```python
from varv.io.labview import read_measurement_dat

raw = read_measurement_dat("experiment_1.dat")

```

Note that this function with downsample the data to a sampling rate of 5 kHz. This can be turned off for variable 
voltage data.

### Custom pandas accesor

#### Finding reads

To find reads in the measurement, run:
```python
from varv.events import Events

events = Events.from_raw(raw)
```

Which returns an ``Events`` object, containing the various reads found in the data. For finding events in 
variable-voltage data, use the keyword arguments:
```python
kwargs = {
    "open_state_current": (170, 200),
    "lowpass": 100,
    "known_good_voltage": (90, 210),
}
eves = Events.from_raw(raw, **kwargs)
```

These events can be filtered by length, step rate, current ranges, and more. They can also be sliced to return single 
events for further analysis:

```python
eve = eves[2]
```

Check out the notebooks folder for more examples.

## Development

For torch on MacOS with Apple Silicon (Uses GPU). For more info, check the [Apple Website](https://developer.apple.com/metal/pytorch/)
```
pip3 install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

### Contribution guidelines

This project follows many principles from the 
[*Good Integration Practices*](https://docs.pytest.org/en/stable/explanation/goodpractices.html) 
from pytest. Important guidelines are:
1. The [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) by The Python 
Packaging Project for building the module.
2. [Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) by pytest for testing.
3. The [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) by Google for names of classes,
variables, etc. Also for the creation of docstrings.
4. The [ruff](https://github.com/astral-sh/ruff) for 
auto-formatting the code.

The symbols ``i``, ``v``, and ``g``, are reserved for current, voltage, and conductance. For indices, the use of ``j`` is preferred.

Finally, this project is inspired by MNE, consider checking out their 
[contribution guideliens](https://mne.tools/1.8/development/contributing.html).


### Testing code

To test the code for the entire module, make sure you are in the ``varv`` directory and simply run:

```shell
pytest
```

Tests for individual submodules can be found in the ``tests`` folder.

### Formatting code

To automatically format the code, use:

```shell
ruff check --fix
```



## Building

```shell
ruff check --fix
```


# References

<a id="1">[1]</a>
Šoštarić , N. (2024). Programming Foundations TU Delft OPEN Publishing.
