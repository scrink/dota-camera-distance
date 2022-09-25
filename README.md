# dota-camera-changer
## About
This application:
1. Locates client.dll file in your Dota folder.
2. Changes camera distance to the value you prefer.
3. Launches Dota 2.

> At first launch you will be prompted to enter the required camera distance. With further launches this app will run Dota with distance you have set initially. You can always change your mind by deleting config.ini generated at the location of the script.

> Replace your Dota 2 icon by this app to completely forget about manually changing camera distance.
## Executing
1. Run ```python main.py```, if you have python installed on your system.
2. Build your own exe file to run on systems without python installed using 
```pyinstaller --noconfirm --onefile --console --clean --icon dota_icon.ico main.py```
3. Download my pre-built .exe from Github releases page
https://github.com/searayeah/dota-camera-changer/releases

