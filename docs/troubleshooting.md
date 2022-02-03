# Troubleshooting


## Install of OQT Python Workers


### Matplotlib


#### Fonts and Freetype

Sometimes `freetype` as to be installed. See the installation documentation of `matplotlib`: https://github.com/matplotlib/matplotlib/blob/master/INSTALL.rst#freetype-and-qhull


#### `On import matplotlib.pyplot as plt: module 'sip' has no attribute 'setapi'`

Install pyqt5: https://www.riverbankcomputing.com/static/Docs/PyQt5/installation.html


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

## Windows

It's best to use WSL2 (https://docs.microsoft.com/en-us/windows/wsl/install-win10). Make sure to have WSL2 installed, not WSL.

Building the database using the Windows command line usually fails, as the files are written for Linux. A simple workaround is to install the app `Ubuntu 20.04 LTS` from the Windows store and run the command for building the database within this app. 
If the building of the database still fails, this usually happens as windows changes file endings. Open the file `\ohsome-quality-analyst\database\init_db.development\schema.dev.sh` in an editor and change the format of line endings to UNIX (LF) (Using Notepad++: `Edit` --> `EOL Conversion` --> `Unix (LF)`).


### Pre commit: ImportError: DLL load failed while importing \_sqlite3: The specified module could not be found.

See this Stackoverflow thread: [Unable to import sqlite3 using Anaconda Python](https://stackoverflow.com/questions/54876404/unable-to-import-sqlite3-using-anaconda-python)
