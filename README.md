# [7.32c/Diretide]dota-camera-distance

*Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.*

[Download latest version](https://github.com/searayeah/dota-camera-distance/releases/download/3.2/dota-camera-distance.exe)

## Abstract
These days people use hex-editors (such as [HxD](https://mh-nexus.de/en/hxd/)) to increase camera distance by editing some hex-string in ```client.dll``` file inside Dota 2 folder. However, camera distance gets reset every time the game gets an update, even a small one. This app provides a solution for this annoying problem.

## App Description
This application:

1. Automatically locates your Dota 2 folder and finds ```client.dll``` file
2. Changes camera distance.
3. Launches Dota 2.

> At first launch you will be prompted to enter the required camera distance. With further launches this app will run Dota with distance you have set initially. You can always change your mind by deleting or editing config.ini generated at the location of the script.

## Executing
1. Run ```python main.py```, if you have [Python](https://www.python.org/) installed on your system.
2. Install [Python](https://www.python.org/downloads/) and [requirements.txt](https://stackoverflow.com/a/15593865) to build your own ```.exe``` file using 
shell```
pyinstaller --noconfirm --onefile --console --clean --icon game-icon.ico --name dota-camera-distance main.py
```
This ```.exe``` file will be usable on systems without Python installed.
3. [Download]() pre-built ```.exe```.

