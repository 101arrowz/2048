# 2048
2048 in Python

Self-contained, cross-platform, works in both Python 2.7 and 3.x. Fully modular. Smooth transitions. Color and font stays true to [the original game](https://github.com/gabrielecirulli/2048). Has a plethora of command-line options, including:
* Custom window size and framerate that comfortably fits _your_ monitor by default
* 3 levels of difficulty
* 

# Pre-requisites
Python and the package `pygame` must be installed.

Download Python (preferably 3.x) from [the Python download page](https://www.python.org/downloads/). If you have a version of Python that comes preinstalled with your operating system, you don't need to install again as long as it is at least 2.7. Install `pygame` by running `pip install pygame` (or `pip3` if you are using Python 3 and are on macOS) from command line.

# Installation
To save the file to your desktop:

On Windows, run the following command in `cmd` (Command Prompt): `powershell.exe (wget https://raw.githubusercontent.com/101arrowz/2048/master/2048.py -OutFile ~\Desktop\2048.py)`

On \*nix/Linux systems (including macOS), run `curl -o ~/Desktop/2048.py 'https://raw.githubusercontent.com/101arrowz/2048/master/2048.py' && chmod 755 ~/Desktop/2048.py` in `bash` (Terminal)

# Important Notes When Running as an Executable
The script, if run with `./2048.py` on \*nix/Linux, will use the default Python interpreter `/usr/bin/env python` at first. If `pygame` is not installed and it is using Python 2, it will automatically try to rerun with Python 3. Therefore, if for some reason you want to force 2048 to use a specific version of Python, change the shebang or install `pygame` on only one version.
