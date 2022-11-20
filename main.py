import configparser
import os
import re
import struct
import time
import traceback
import winreg
import vdf
import requests

DOTA_APP_ID = "570"
DEFAULT_SEARCH_HEX_STRING = "00 00 00 00 00 00 2E 40 00 00 96 44 00 00 E1 44"
SERVER_SEARCH_HEX_STRING_LINK = "https://raw.githubusercontent.com/searayeah/dota-camera-distance/online-hex-code-update/current_hex_string"
DEFAULT_DISTANCE = "1200"
STEAM_REGISTRY_KEY = "SOFTWARE\\WOW6432Node\\Valve\\Steam"
CLIENT_DLL_PATH = "\\steamapps\\common\\dota 2 beta\\game\\dota\\bin\\win64\\client.dll"
LIBRARY_FOLDERS_PATH = "\\steamapps\\libraryfolders.vdf"
APP_MANIFEST_PATH = f"\\steamapps\\appmanifest_{DOTA_APP_ID}.acf"


def set_distance(search_hex_string, distance, client_dll_path):
    search_hex_string = search_hex_string.lower().replace(" ", "")
    default_distance_hex = struct.pack("f", float(DEFAULT_DISTANCE)).hex()
    distance_hex = struct.pack("f", float(distance)).hex()

    # should always be 8, so this might be unnecessary
    distance_hex_length = len(distance_hex)

    # finding the location of default distance(00 00 96 44 = 1200) in search hex line
    distance_index = search_hex_string.find(default_distance_hex)

    # regex string that is invulnerable to distance changes
    search_hex_string_regex = re.compile(
        search_hex_string[:distance_index]
        + f"\w{{{distance_hex_length}}}"  # regex \w{8} means any 8 characters [a-zA-Z0-9_]
        + search_hex_string[distance_index + distance_hex_length :]
    )

    distance_hex_string = (
        search_hex_string[:distance_index]
        + distance_hex
        + search_hex_string[distance_index + distance_hex_length :]
    )

    with open(client_dll_path, "rb") as f:
        client_dll_hex = f.read().hex()

    client_dll_hex_new, changes_count = re.subn(
        search_hex_string_regex, distance_hex_string, client_dll_hex, 1
    )

    if changes_count == 0:
        raise Exception(
            "Couldn't find the hex value in client.dll file. Valve might have changed it."
        )

    print(f"Old: {re.search(search_hex_string_regex, client_dll_hex).group()}")
    print(f"New: {re.search(search_hex_string_regex, client_dll_hex_new).group()}")

    with open(client_dll_path, "wb") as f:
        f.write(bytes.fromhex(client_dll_hex_new))


def get_steam_path():
    # Getting steam path from Windows Registry
    hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY)
    steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
    winreg.CloseKey(hkey)
    return steam_path


def get_steam_library_path(steam_path):
    # Getting steam library path,
    # as Dota 2 can be installed on different drive
    library_folders = vdf.load(open(steam_path + LIBRARY_FOLDERS_PATH))[
        "libraryfolders"
    ]
    for key in library_folders:
        if str(DOTA_APP_ID) in library_folders[key]["apps"]:
            return library_folders[key]["path"]


def dota_was_updating(steam_library_path):
    # Dota 2 update status are stored in app_manifest file
    # If status is '4' that means that Dota is updated and ready to launch
    # Otherwise, it is needed to wait for it to end its updates
    app_manifest = vdf.load(open(steam_library_path + APP_MANIFEST_PATH))
    app_status = app_manifest["AppState"]["StateFlags"]
    if app_status != "4":
        while app_status != "4":
            print(f"Waiting for Dota 2 to get updates, status: {app_status}", end="\r")
            time.sleep(1)
            app_manifest = vdf.load(open(steam_library_path + APP_MANIFEST_PATH))
            app_status = app_manifest["AppState"]["StateFlags"]
        print()
        return True
    else:
        return False


def get_current_hex_string():
    try:
        response = requests.get(SERVER_SEARCH_HEX_STRING_LINK)
        response.raise_for_status()
        print("String received from GitHub")
        return response.text
    except requests.exceptions.RequestException as e:
        print(e)
        print("Couldn't receive string from GitHub, using the default one")
        return DEFAULT_SEARCH_HEX_STRING


def set_config():
    config_path = os.path.join(os.getcwd(), "config.ini")
    config_file = configparser.ConfigParser()
    config_file.read(config_path)

    if "DOTA-CAMERA-DISTANCE" not in config_file:
        config_file["DOTA-CAMERA-DISTANCE"] = {}

    config = config_file["DOTA-CAMERA-DISTANCE"]

    if "receive_type" not in config or not config["receive_type"]:
        config[
            '# "auto"'
        ] = 'automatically get string, "manual" = set the string manually'
        config["receive_type"] = "auto"
    print(f"Receive type: {config['receive_type']}")

    # I will update the string through github current_hex_string file
    # but if you obtained the new string faster than me, you can
    # set this config variable to "manual", set your manual string, and the program won't update it
    # automatically every time you launch it.
    if (
        (config["receive_type"].lower() == "auto")
        or "search_hex_string" not in config
        or not config["search_hex_string"]
    ):
        config["search_hex_string"] = get_current_hex_string()
    print(f"Search hex string: {config['search_hex_string']}")

    if "distance" not in config or not config["distance"]:
        config["distance"] = (
            input("Enter distance[default 1200, recommended 1400]: ")
            or DEFAULT_DISTANCE
        )
    print(f"Distance: {config['distance']}")

    if "steam_path" not in config or not config["steam_path"]:
        config["steam_path"] = get_steam_path()
    print(f"Steam path: {config['steam_path']}")

    if "steam_library_path" not in config or not config["steam_library_path"]:
        config["steam_library_path"] = get_steam_library_path(config["steam_path"])
    print(f"Steam library path: {config['steam_library_path']}")

    if "client_dll_path" not in config or not config["client_dll_path"]:
        config["client_dll_path"] = config["steam_library_path"] + CLIENT_DLL_PATH
    print(f"Client.dll path: {config['client_dll_path']}")

    with open(config_path, "w") as configfile:
        config_file.write(configfile)
    print(f"Updated {config_path}")

    return (
        config["receive_type"],
        config["search_hex_string"],
        config["distance"],
        config["steam_path"],
        config["steam_library_path"],
        config["client_dll_path"],
    )


def main():
    (
        receive_type,
        search_hex_string,
        distance,
        steam_path,
        steam_library_path,
        client_dll_path,
    ) = set_config()

    set_distance(search_hex_string, distance, client_dll_path)
    os.startfile(f"steam://rungameid/{DOTA_APP_ID}")  # windows only
    print("Launching Dota 2 ...")

    # When launching Dota for the first time it might get updates,
    # so client.dll needs to be rewritten again
    if dota_was_updating(steam_library_path):
        set_distance(search_hex_string, distance, client_dll_path)
        print('Press "Play game"')


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print(
            "Program crashed, send me a screenshot via "
            + "https://github.com/searayeah/dota-camera-distance/issues"
        )
    finally:
        for i in range(5, 0, -1):
            print(f"Exit in: {i}", end="\r")
            time.sleep(1)
