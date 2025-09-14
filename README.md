[![Python version: 3.11--3.13](https://img.shields.io/badge/python%20version-3.11,%203.13-1464b4.svg)](https://www.python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Pressure-Volume analysis (RV) for cardiology #

This repository contains that analysis time-series data for pressure and volume
(right-ventricular measurements). This involves:

- automatic recognition of cycles
- fitting/re-fitting of models
- automatic recognition of 'special points' (of physical interest)
- automatic matching of the pressure and volume series
- output of tables and plots (individual time-series and P-V plots).

The code handles unit conversions (input -> internal usage -> outputs)
robustly using the python package [pint](https://pint.readthedocs.io).

## Examples and technical notes ##

See [examples](examples) and [notes](docs/README.md).

## System requirements ##

- [Python ^3.11](https://www.python.org/downloads) (currently developed under 3.13)

- [Justfile tool](https://github.com/casey/just#installation)

### Windows users ###

Windows users are encouraged to install **bash**.
There are a few ways to do this:

1. Install [git for windows](https://gitforwindows.org) (which includes bash).

2. [Activate ubuntu](https://devblogs.microsoft.com/commandline/bash-on-ubuntu-on-windows-download-now-3).
   This is perhaps more standard, but more complicated.

To install the **Justfile tool** you may need to install
[chocolatey](https://chocolatey.org/install)
or [scoop](https://github.com/ScoopInstaller/Scoop#installation).
And then install the tool via these
(see <https://github.com/casey/just#installation>).

## Usage ##

All **bash** commands are to be run from the **root** folder of this repository.

1. Initialisation (only needed once)
  Open a **bash** terminal and execute

    ```bash
    just build
    ```

    If there are any errors, run this once more.
    If this still persists, contact the maintainer.

2. Add your Data e.g. to the [data](data) folder.

3. Configuration:

    - Adjust the file [setup/config.yaml](setup/config.yaml).
    - If this does not exist, copy the file form [templates/templates-config.yaml](templates/template-config.yaml)
     to `setup/config.yaml`.
    - Ensure in particular that the paths to the input and output data are set correctly.
    - For the output plots choose `*.html` format for dynamical output,
      otherwise choose `*.png` (lossless).

4. _Either_

    - (interactive) open [notebooks/main.ipynb](notebooks/main.ipynb)
      and run all cells; _or_

    - (non-interactive) execute in a **bash** terminal

        ```bash
        just run
        ```

## Clean state ##

If there are issues, it often helps to restore things to a fresh state.
To do this for your local copy of the repository, run

```bash
just clean
```

NOTE: After running this, you will need to run `just build` before executing the code again.

If you just wish to obtain a fresh state for the notebooks, run

```bash
just clean-notebooks
```

## Development ##

See [CONTRIBUTING.md](CONTRIBUTING.md).

## References ##

The structure of the code in this repository is entirely the work of the owner.
Some methods in this repository (e.g. the automatic recognition of cycles)
are in part inspired by literature, e.g. [^Heerdt2019].
The remaining methods (esp. polynomial fitting methods)
and corresponding code in this repository
was developed independently by the repository owner.

[^Heerdt2019]: Heerdt, Paul M et al. "A pressure-based single beat method for estimation of right ventricular ejection fraction: proof of concept." _The European respiratory journal_ vol. 55,3 1901635. 12 Mar. 2020, doi:10.1183/13993003.01635-2019
