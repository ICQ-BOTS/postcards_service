import vanilla_images_gen
import xmlrpc.client
from PIL import Image, ImageDraw
from io import BytesIO
import time
import configparser
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f"{SCRIPT_PATH}/config.ini")

HOST_IP = config.get("main", "host")
HOST_PORT = config.get("main", "port")

GEN_DELAY = config.get("generation", "delay")


def run():
    server = xmlrpc.client.ServerProxy(f"http://{HOST_IP}:{HOST_PORT}")

    while True:
        actual_array = server.get_actual_vanilla()
        print(f"Regen: {actual_array}")

        postcard_index = actual_array[0]
        if postcard_index != -1:
            postcards = vanilla_images_gen.gen_image()
            data_array = []
            for postcard in postcards:
                byte_io = BytesIO()
                postcard.save(byte_io, "JPEG")
                byte_io.seek(0)
                data_array.append(xmlrpc.client.Binary(byte_io.read()))

            server.vanilla_write_image(data_array, postcard_index)
            time.sleep(0.01)
        else:
            time.sleep(2)


if __name__ == "__main__":
    run()
