from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc
import xmlrpc.client
from PIL import Image, ImageDraw

import random_picture
from io import BytesIO
import configparser
import db
import os
import shutil

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f"{SCRIPT_PATH}/config.ini")

HOST_IP = config.get("main", "host")
HOST_PORT = config.get("main", "port")

DB_HOST = config.get("tarantool", "db_host")
DB_PORT = config.get("tarantool", "db_port")

GEN_DELAY = config.get("generation", "delay")
POSTCARDS_PER_NOUN = config.get("generation", "postcards_per_noun")
VANILLA_POSTCARDS_COUNT = config.get("generation", "vanilla_postcards_count")

# Restrict to a particular path.


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


class RPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.handle_next = True
        while self.handle_next:
            self.handle_request()

    def stop(self):
        self.handle_next = False


# Create server
server = RPCServer(
    (HOST_IP, int(HOST_PORT)), requestHandler=RequestHandler, allow_none=True
)
server.register_introspection_functions()

db.connect(DB_HOST, DB_PORT)
db_nouns_ids_dict = db.start_init(
    random_picture.nouns, int(POSTCARDS_PER_NOUN), int(VANILLA_POSTCARDS_COUNT)
)
db_ids_nouns_dict = {}
for key, value in db_nouns_ids_dict.items():
    db_ids_nouns_dict[value] = key

# fiesta_bot


def get_random_postcard(user_id):
    db_result = db.get_random_postcard(user_id)
    image_file = open(
        os.path.join(SCRIPT_PATH, "postcards", f"{db_result[0]}/{db_result[1]}_2.jpg"),
        "rb",
    )
    file_data = image_file.read()
    image_file.close()
    return xmlrpc.client.Binary(file_data)


server.register_function(get_random_postcard)

# fiesta_bot


def get_random_noun_postcard(user_id, noun_id):
    db_result = db.get_random_noun_postcard(user_id, noun_id)
    image_file = open(
        os.path.join(SCRIPT_PATH, "postcards", f"{noun_id}/{db_result[0]}_1.jpg"), "rb"
    )
    file_data = image_file.read()
    image_file.close()
    return xmlrpc.client.Binary(file_data)


server.register_function(get_random_noun_postcard)


def get_nouns_ids_dict():
    global db_nouns_ids_dict
    return db_nouns_ids_dict


server.register_function(get_nouns_ids_dict)


def get_actual():
    result = db.get_generate_priority().data
    return result


server.register_function(get_actual)


def write_image(data_array, noun_id, postcard_index):
    counter = 1
    for image_data in data_array:
        image_file = open(
            os.path.join(
                SCRIPT_PATH,
                "postcards",
                str(noun_id),
                f"{postcard_index}_{counter}.jpg",
            ),
            "wb",
        )
        image_file.write(image_data.data)
        image_file.close()
        counter += 1

    db.postcard_showings_dec(noun_id, postcard_index)


server.register_function(write_image)

# ------------------------Vanila postcards--------------------------------


def get_actual_vanilla():
    result = db.get_vanilla_generate_priority().data
    return result


server.register_function(get_actual_vanilla)


def get_random_vanilla_postcard(user_id, watermark_index):
    db_result = db.get_random_vanilla_postcard(user_id)
    image_path = os.path.join(
        SCRIPT_PATH, "vanilla_postcards", f"{db_result[0]}_{watermark_index}.jpg"
    )
    image_file = open(image_path, "rb")
    file_data = image_file.read()
    image_file.close()

    return xmlrpc.client.Binary(file_data)


server.register_function(get_random_vanilla_postcard)


def vanilla_write_image(data_array, index):
    counter = 1
    for image_data in data_array:
        image_file = open(
            os.path.join(SCRIPT_PATH, "vanilla_postcards", f"{index}_{counter}.jpg"),
            "wb",
        )
        image_file.write(image_data.data)
        image_file.close()
        counter += 1

    db.vanilla_postcard_showings_dec(index)


server.register_function(vanilla_write_image)


def stop_service():
    print("exit")
    server.stop()


server.register_function(stop_service)


# Run the server's main loop
server.serve_forever()
