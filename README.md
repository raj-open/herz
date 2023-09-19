# PV-Loops #

This repository contains code to extract time-series data for pressure and volume,
align these and produce pressure-volume data series and plots.
Methods are developed in [^Heerdt2019].

## System requirements ##

- [Python 3.10+](https://www.python.org/downloads)
- [Justfile tool](https://github.com/casey/just#installation)
- (development only) [Node and npm](https://nodejs.org/en/download/current)

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

2. Add your Data e.g. to the [./data](data) folder.

3. Configuration:

    - Adjust the file [./setup/config.yaml](setup/config.yaml).
    - If this does not exist, copy the file form [./templates/templates-config.yaml](templates/template-config.yaml)
     to `setup/config.yaml`.
    - Ensure in particular that the paths to the input and output data are set correctly.
    - For the output plots choose `*.html` format for dynamical output,
      otherwise choose `*.png` (lossless).

4. _Either_

    - Open the notebook [./notebooks/main.ipynb](notebooks/main.ipynb) and run all cells.

    - Run (non-interactive) in a **bash** terminal

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

[^Heerdt2019]: Heerdt, Paul M et al. "A pressure-based single beat method for estimation of right ventricular ejection fraction: proof of concept." _The European respiratory journal_ vol. 55,3 1901635. 12 Mar. 2020, doi:10.1183/13993003.01635-2019
