# [7.32c]dota-camera-distance
*Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.*

[Download latest version](https://github.com/searayeah/dota-camera-distance/releases/download/3.1/dota-camera-distance.exe)

## Abstract
These days people use a hex-editor (such as [HxD](https://mh-nexus.de/en/hxd/)) to increase camera distance by editing some hex-value in ```client.dll``` file inside Dota 2 folder. However, the value gets reset every time the game gets an update, even a small one(bug fixes, etc.). This app is for making life easier by not having to manually do this every day(Dota gets updates almost every single day).
## App Description
This application:
1. Automatically locates your Dota 2 folder and finds ```client.dll``` file
2. Changes camera distance to the value you prefer.
3. Launches Dota 2.
> At first launch you will be prompted to enter the required camera distance. With further launches this app will run Dota with distance you have set initially. You can always change your mind by deleting or editing config.ini generated at the location of the script.
## Executing
1. Run ```python main.py```, if you have Python installed on your system.
2. Install [Python](https://www.python.org/downloads/) and [requirements](https://stackoverflow.com/a/15593865) to build your own ```.exe``` file to run on systems without python installed using 
```pyinstaller --noconfirm --onefile --console --clean --icon app/game-icon.ico --name dota-camera-distance app/main.py```.
3. Download pre-built ```.exe``` from [Github releases page](https://github.com/searayeah/dota-camera-changer/releases).

