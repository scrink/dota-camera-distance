# https://stackoverflow.com/questions/19414847/how-to-convert-floating-point-number-in-python
# https://stackoverflow.com/questions/34687516/how-to-read-binary-files-as-hex-in-python
# https://pythontic.com/containers/bytes/hex
# https://stackoverflow.com/questions/5649407/hexadecimal-string-to-byte-array-in-python
# 00 00 96 44 00 40 9C 44 00 80 A2 44 00 80 B4 44
# https://www.youtube.com/watch?v=GNOkvm5MrB0

import struct
import configparser
import os


def main():
    cwd = os.getcwd()
    config = configparser.ConfigParser()
    config.read(cwd + "/config.ini")
    search_value = (
        config["DOTA-CAMERA-CHANGER"]["current_patch_search_value"]
        .lower()
        .replace(" ", "")
    )
    desired_distance = float(config["DOTA-CAMERA-CHANGER"]["desired_distance"])
    client_dll_path = config["DOTA-CAMERA-CHANGER"]["client_dll_path"]

    hex_distance = struct.pack("f", desired_distance).hex()

    with open(client_dll_path, "rb") as f:
        hexdata = f.read().hex()
        camera_hex_index = hexdata.find(search_value)
        if camera_hex_index == -1:
            print("It seems that valve changed camera hex code")
            return
        hexdata = (
            hexdata[0 : camera_hex_index - 8]
            + hex_distance
            + hexdata[camera_hex_index:]
        )
    with open(client_dll_path, "wb") as f:
        f.write(bytes.fromhex(hexdata))
    os.startfile("steam://rungameid/570")


if __name__ == "__main__":
    main()
