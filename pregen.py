import random_picture
import db
import configparser
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
POSTCARDS_PATH = os.path.join(SCRIPT_PATH, "postcards")

config = configparser.ConfigParser()
config.read("config.ini")

HOST_IP = config.get("main", "host")
HOST_PORT = config.get("main", "port")

DB_HOST = config.get("tarantool", "db_host")
DB_PORT = config.get("tarantool", "db_port")

GEN_DELAY = config.get("generation", "delay")
POSTCARDS_PER_NOUN = config.get("generation", "postcards_per_noun")
VANILLA_POSTCARDS_COUNT = config.get("generation", "vanilla_postcards_count")

db.connect(DB_HOST, DB_PORT)

if not os.path.exists(POSTCARDS_PATH):
    os.makedirs(POSTCARDS_PATH)


db.start_init(
    random_picture.nouns, int(POSTCARDS_PER_NOUN), int(VANILLA_POSTCARDS_COUNT)
)

counter = 1
for noun_description in random_picture.nouns:
    path = os.path.join(POSTCARDS_PATH, str(noun_description["db_id"]))
    if not os.path.exists(path):
        os.makedirs(path)
    print(f"{counter}. Start for {noun_description['word']}")
    for image_index in range(int(POSTCARDS_PER_NOUN)):

        images_array = random_picture.gen_postcard(noun_description)
        image_counter = 1
        for image in images_array:
            image_path = os.path.join(path, f"{image_index}_{image_counter}.jpg")
            if os.path.exists(image_path):
                os.remove(image_path)
            image.save(image_path, "JPEG")
            image_counter += 1
    counter += 1

db.disconnect()
