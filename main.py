import struct
import configparser
import os
import vdf
from time import sleep
import winreg
import traceback

DOTA_APP_ID = "570"
SEARCH_VALUE = "00 40 9C 44 00 80 A2 44 00 80 B4 44"
DEFAULT_DISTANCE = "1200"
STEAM_REGISTRY_KEY = "SOFTWARE\\WOW6432Node\\Valve\\Steam"
CLIENT_DLL_DEFAULT_PATH = (
    "\\steamapps\\common\\dota 2 beta\\game\\dota\\bin\\win64\\client.dll"
)
LIBRARY_PATH = "\\steamapps\\libraryfolders.vdf"


def main():
    cwd = os.getcwd()
    config = configparser.ConfigParser()
    config.read(cwd + "\\config.ini")

    if "DOTA-CAMERA-CHANGER" not in config:
        config["DOTA-CAMERA-CHANGER"] = {}

    changer_cfg = config["DOTA-CAMERA-CHANGER"]

    if "search_value" not in changer_cfg or not changer_cfg["search_value"]:
        changer_cfg["search_value"] = SEARCH_VALUE

    if "distance" not in changer_cfg or not changer_cfg["distance"]:
        changer_cfg["distance"] = (
            input("Enter distance[default 1200, recommended 1400]: ")
            or DEFAULT_DISTANCE
        )

    if "client_dll_path" not in changer_cfg or not changer_cfg["client_dll_path"]:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY)
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
        winreg.CloseKey(hkey)

        library_folders = vdf.load(open(steam_path + LIBRARY_PATH))["libraryfolders"]
        for key in library_folders:
            if str(DOTA_APP_ID) in library_folders[key]["apps"]:
                changer_cfg["client_dll_path"] = (
                    library_folders[key]["path"] + CLIENT_DLL_DEFAULT_PATH
                )

        print(f"client_dll_path: {changer_cfg['client_dll_path']}")

    with open(cwd + "\\config.ini", "w") as configfile:
        config.write(configfile)

    search_value = changer_cfg["search_value"].lower().replace(" ", "")
    hex_distance = struct.pack("f", float(changer_cfg["distance"])).hex()

    with open(changer_cfg["client_dll_path"], "rb") as f:

        hexdata = f.read().hex()
        camera_hex_index = hexdata.find(search_value)
        if camera_hex_index == -1:
            raise Exception("It seems that valve changed camera hex code")

        print(f"OLD: {hexdata[camera_hex_index - 8:camera_hex_index]}")
        hexdata = (
            hexdata[0 : camera_hex_index - 8]
            + hex_distance
            + hexdata[camera_hex_index:]
        )
        print(f"NEW: {hexdata[camera_hex_index - 8:camera_hex_index]}")

    with open(changer_cfg["client_dll_path"], "wb") as f:
        f.write(bytes.fromhex(hexdata))

    os.startfile("steam://rungameid/570")  # windows only
    print("SUCCESS")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
    finally:
        for i in range(5, 0, -1):
            print(f"Exit in: {i}", end="\r")
            sleep(1)
