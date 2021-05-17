# Troubleshooting


## Install of OQT Python Workers


### Matplotlib


#### Fonts and Freetype

Sometimes `freetype` as to be installed. See the installation documentation of `matplotlib`: https://github.com/matplotlib/matplotlib/blob/master/INSTALL.rst#freetype-and-qhull


#### `On import matplotlib.pyplot as plt: module 'sip' has no attribute 'setapi'`

Install pyqt5: https://www.riverbankcomputing.com/static/Docs/PyQt5/installation.html


## Windows

It's best to use WSL2 (https://docs.microsoft.com/en-us/windows/wsl/install-win10). Make sure to have WSL2 installed, not WSL.
Docker on Windows WSL:


### Pre commit: ImportError: DLL load failed while importing \_sqlite3: The specified module could not be found.

See this Stackoverflow thread: [Unable to import sqlite3 using Anaconda Python](https://stackoverflow.com/questions/54876404/unable-to-import-sqlite3-using-anaconda-python)
