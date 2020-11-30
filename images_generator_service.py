import random_picture
import xmlrpc.client
from PIL import Image, ImageDraw
from io import BytesIO
import time
import configparser
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f"{SCRIPT_PATH}/config.ini")

HOST_IP = config.get('main', 'host')
HOST_PORT = config.get('main', 'port')

GEN_DELAY = config.get('generation', 'delay')


def run():
    server = xmlrpc.client.ServerProxy(f'http://{HOST_IP}:{HOST_PORT}')

    nouns_ids_dict = server.get_nouns_ids_dict()
    ids_nouns_dict = {}
    for key, value in nouns_ids_dict.items():
        ids_nouns_dict[value] = key

    while True:
        actual_array = server.get_actual()
        print(f'Regen: {actual_array}')

        noun_id = actual_array[0]
        if noun_id != -1:
            noun_word = ids_nouns_dict[noun_id]
            postcard_index = actual_array[1]
            description = random_picture.find_word_description(
                random_picture.nouns, noun_word)
            postcards = random_picture.gen_postcard(description)

            data_array = []
            for postcard in postcards:
                byte_io = BytesIO()
                postcard.save(byte_io, "JPEG")
                byte_io.seek(0)
                data_array.append(xmlrpc.client.Binary(byte_io.read()))

            server.write_image(data_array, noun_id, postcard_index)
            time.sleep(0.01)
        else:
            time.sleep(2)


if __name__ == '__main__':
    run()
