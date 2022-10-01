import struct
import configparser
import os
import vdf
import time
import winreg
import traceback

DOTA_APP_ID = "570"
SEARCH_VALUE = "00 00 96 44 00 40 9C 44 00 80 A2 44 00 80 B4 44"
DEFAULT_DISTANCE = "1200"
STEAM_REGISTRY_KEY = "SOFTWARE\\WOW6432Node\\Valve\\Steam"
CLIENT_DLL_DEFAULT_PATH = (
    "\\steamapps\\common\\dota 2 beta\\game\\dota\\bin\\win64\\client.dll"
)
LIBRARY_FOLDERS_PATH = "\\steamapps\\libraryfolders.vdf"
APP_MANIFEST_PATH = f"\\steamapps\\appmanifest_{DOTA_APP_ID}.acf"


def set_distance(changer_cfg):
    search_value = changer_cfg["search_value"].lower().replace(" ", "")[8:]
    hex_distance = struct.pack("f", float(changer_cfg["distance"])).hex()

    with open(changer_cfg["client_dll_path"], "rb") as f:
        hexdata = f.read().hex()
        camera_hex_index = hexdata.find(search_value)
        if camera_hex_index == -1:
            raise Exception("It seems that Valve have changed camera hex code")

        print(f"Old value: {hexdata[camera_hex_index -8 :camera_hex_index]}")
        hexdata = (
            hexdata[0 : camera_hex_index - 8]
            + hex_distance
            + hexdata[camera_hex_index:]
        )
        print(f"New value: {hexdata[camera_hex_index-8:camera_hex_index]}")

    with open(changer_cfg["client_dll_path"], "wb") as f:
        f.write(bytes.fromhex(hexdata))


def main():
    cwd = os.getcwd()
    config = configparser.ConfigParser()
    config.read(cwd + "\\config.ini")

    if "DOTA-CAMERA-DISTANCE" not in config:
        config["DOTA-CAMERA-DISTANCE"] = {}

    changer_cfg = config["DOTA-CAMERA-DISTANCE"]

    if "search_value" not in changer_cfg or not changer_cfg["search_value"]:
        changer_cfg["search_value"] = SEARCH_VALUE
    print(f"Search value: {changer_cfg['search_value']}")

    if "distance" not in changer_cfg or not changer_cfg["distance"]:
        changer_cfg["distance"] = (
            input("Enter distance[default 1200, recommended 1400]: ")
            or DEFAULT_DISTANCE
        )
    print(f"Distance: {changer_cfg['distance']}")

    if "steam_path" not in changer_cfg or not changer_cfg["steam_path"]:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY)
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
        winreg.CloseKey(hkey)
        changer_cfg["steam_path"] = steam_path
    print(f"Steam path: {changer_cfg['steam_path']}")

    if "steam_library_path" not in changer_cfg or not changer_cfg["steam_library_path"]:
        library_folders = vdf.load(
            open(changer_cfg["steam_path"] + LIBRARY_FOLDERS_PATH)
        )["libraryfolders"]
        for key in library_folders:
            if str(DOTA_APP_ID) in library_folders[key]["apps"]:
                changer_cfg["steam_library_path"] = library_folders[key]["path"]
    print(f"Steam library path: {changer_cfg['steam_library_path']}")

    if "client_dll_path" not in changer_cfg or not changer_cfg["client_dll_path"]:
        changer_cfg["client_dll_path"] = (
            changer_cfg["steam_library_path"] + CLIENT_DLL_DEFAULT_PATH
        )
    print(f"Client.dll path: {changer_cfg['client_dll_path']}")

    with open(cwd + "\\config.ini", "w") as configfile:
        config.write(configfile)
        print("Updated: config.ini")

    set_distance(changer_cfg)
    os.startfile("steam://rungameid/{DOTA_APP_ID}")  # windows only
    print("Launching Dota 2 ...")

    app_manifest = vdf.load(open(changer_cfg["steam_library_path"] + APP_MANIFEST_PATH))
    app_status = app_manifest["AppState"]["StateFlags"]
    if app_status != "4":
        while app_status != "4":
            print(f"Waiting for Dota 2 to get updates, status: {app_status}", end="\r")
            time.sleep(3)
            app_manifest = vdf.load(
                open(changer_cfg["steam_library_path"] + APP_MANIFEST_PATH)
            )
            app_status = app_manifest["AppState"]["StateFlags"]
        print()
        set_distance(changer_cfg)
        print('Press "Play game"')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print(
            "Program crashed, send me a screenshot and config.ini "
            + "contents via https://github.com/searayeah/dota-camera-distance/issues"
        )
    finally:
        for i in range(5, 0, -1):
            print(f"Exit in: {i}", end="\r")
            time.sleep(1)
