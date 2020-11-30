import random_picture
import db
import configparser
import os
import vanilla_images_gen

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read("config.ini")

HOST_IP = config.get("main", "host")
HOST_PORT = config.get("main", "port")

DB_HOST = config.get("tarantool", "db_host")
DB_PORT = config.get("tarantool", "db_port")

GEN_DELAY = config.get("generation", "delay")
POSTCARDS_PER_NOUN = config.get("generation", "postcards_per_noun")
VANILA_POSTCARDS_COUNT = config.get("generation", "vanilla_postcards_count")

db.connect(DB_HOST, DB_PORT)
db.start_init(
    random_picture.nouns, int(POSTCARDS_PER_NOUN), int(VANILA_POSTCARDS_COUNT)
)

VANILA_IMAGES_PATH = os.path.join(SCRIPT_PATH, "vanilla_postcards")

if not os.path.exists(VANILA_IMAGES_PATH):
    os.makedirs(VANILA_IMAGES_PATH)

counter = 1

for image_index in range(int(VANILA_POSTCARDS_COUNT)):
    print(f"{image_index}")
    images_array = vanilla_images_gen.gen_image()
    image_counter = 1
    for image in images_array:
        image_path = os.path.join(
            VANILA_IMAGES_PATH, f"{image_index}_{image_counter}.jpg"
        )
        if os.path.exists(image_path):
            os.remove(image_path)
        image.save(image_path, "JPEG")
        image_counter += 1

db.disconnect()
