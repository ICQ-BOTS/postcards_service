import tarantool


def connect(host, port):
    global connection
    connection = tarantool.connect(host, int(port))


def disconnect():
    global connection
    connection.close()


def start_init(nouns_descriptions, postcards_per_noun, vanilla_postcards_count):
    nouns_list = []
    for noun_description in nouns_descriptions:
        nouns_list.append(noun_description["word"])

    ids_dict = connection.call(
        "start_init", nouns_list, postcards_per_noun, vanilla_postcards_count
    ).data[0]

    for noun_description in nouns_descriptions:
        noun_description["db_id"] = ids_dict[noun_description["word"]]

    return ids_dict


# --------------------------------Postcards--------------------------------


def get_generate_priority():
    global connection
    return connection.call("get_generate_priority")


def postcard_showings_dec(noun_id, postcard_index):
    global connection
    return connection.call("postcard_showings_dec", noun_id, postcard_index)


def get_random_postcard(user_id):
    global connection
    return connection.call("get_next_random_postcard", user_id).data


def get_random_noun_postcard(user_id, noun_id):
    global connection
    return connection.call("get_next_random_noun_postcard", user_id, noun_id).data


# --------------------------------Vanila postcards--------------------------------


def get_vanilla_generate_priority():
    global connection
    return connection.call("get_vanilla_generate_priority")


def get_random_vanilla_postcard(user_id):
    global connection
    return connection.call("get_next_random_vanilla_postcard", user_id).data


def vanilla_postcard_showings_dec(postcard_index):
    global connection
    return connection.call("vanilla_postcard_showings_dec", postcard_index)
