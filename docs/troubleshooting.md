# Troubleshooting

## OQT Installation

### scikit-learn

During installation of scikit-learn following error can arise:
```
    [...]
    numpy.distutils.system_info.NotFoundError: No BLAS/LAPACK libraries found.
    To build Scipy from sources, BLAS & LAPACK libraries need to be installed.
    See site.cfg.example in the Scipy source directory and
    https://docs.scipy.org/doc/scipy/reference/building/index.html for details.
```

Install BLAS and LAPACK on your system to fix this error:

Debian/Ubuntu: `sudo apt-get install libblas-dev liblapack-dev`
Fedora/Red Hat: `sudo dnf install blas-devel lapack-devel`

## Windows Setup

It's best to use WSL2 (https://docs.microsoft.com/en-us/windows/wsl/install-win10). Make sure to have WSL2 installed, not WSL.

### Pre commit: ImportError: DLL load failed while importing \_sqlite3: The specified module could not be found.

See this Stackoverflow thread: [Unable to import sqlite3 using Anaconda Python](https://stackoverflow.com/questions/54876404/unable-to-import-sqlite3-using-anaconda-python)
