import pymorphy2
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib
from lxml import html
import os
import random
import zlib
import re
import logging

import numpy
from PIL import Image, ImageDraw
from PIL import ImageFont

import math
import colorsys
import matplotlib
import os
import os.path

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

SCRIPT_PATH

log = logging.getLogger(__name__)

translator = Translator()
morph = pymorphy2.MorphAnalyzer()

max_pages = 2

WATERMARK_BOTTOM_OFFSET = 66
executor = ThreadPoolExecutor(max_workers=10)

nouns = [
    {"word": "компьютер"},
    {"word": "апельсин"},
    {"word": "трава"},
    {"word": "торт"},
    {"word": "хлеб"},
    {"word": "мёд"},
    {"word": "пчела"},
    {"word": "мышь"},
    {"word": "слон"},
    {"word": "планета"},
    {"word": "письмо"},
    {"word": "стол"},
    {"word": "стул"},
    {"word": "золото"},
    {"word": "кот"},
    {"word": "буква"},
    {"word": "лимон"},
    {"word": "скотч"},
    {"word": "яблоко"},
    {"word": "футболка"},
    {"word": "коробка"},
    {"word": "кружка"},
    {"word": "омлет"},
    {"word": "блинчик"},
    {"word": "кролик"},
    {"word": "телефон"},
    {"word": "снежинка"},
    {"word": "часы"},
    {"word": "стрелка"},
    {"word": "кофе"},
    {"word": "барабан"},
    {"word": "свеча"},
    {"word": "костёр"},
    {"word": "поход"},
    {"word": "шарик"},
    {"word": "мяч"},
    {"word": "кубик"},
    {"word": "тарелка"},
    {"word": "спагетти"},
    {"word": "смайлик"},
    {"word": "сосулька"},
    {"word": "конфета"},
    {"word": "лошадь"},
    {"word": "ракушка"},
    {"word": "шляпа"},
    {"word": "куртка"},
    {"word": "самолёт"},
    {"word": "вертолёт"},
    {"word": "машина"},
    {"word": "ракета"},
    {"word": "поезд"},
    {"word": "динозавр"},
    {"word": "стикер"},
    {"word": "цветок"},
    {"word": "парик"},
    {"word": "робот"},
    {"word": "рука"},
    {"word": "корова"},
    {"word": "лапа"},
    {"word": "корона"},
    {"word": "книга"},
    {"word": "парашют"},
    {"word": "птица"},
    {"word": "лампа"},
    {"word": "перчатка"},
    {"word": "рыба"},
    {"word": "молоко"},
    {"word": "олень"},
    {"word": "принтер"},
    {"word": "шоколад"},
    {"word": "кисть"},
    {"word": "карандаш"},
    {"word": "ручка"},
    {"word": "статуя"},
    {"word": "бабочка"},
    {"word": "лемон"},
    {"word": "конверт"},
    {"word": "черепаха"},
    {"word": "автомобиль"},
    {"word": "люстра"},
    {"word": "дуб"},
    {"word": "сосна"},
    {"word": "береза"},
    {"word": "роза"},
    {"word": "ромашка"},
    {"word": "велосипед"},
    {"word": "елка"},
    {"word": "такси"},
    {"word": "сумка"},
    {"word": "окно"},
    {"word": "глаз"},
    {"word": "нос"},
    {"word": "рот"},
    {"word": "ухо"},
    {"word": "нога"},
    {"word": "глаз"},
    {"word": "стопа"},
    {"word": "морковка"},
    {"word": "смайлик"},
    {"word": "сосна"},
]

themes = [
    {"ледяной", "снежный", "холодный", "зимний"},
    {"весенний", "трава"},
    {"морской", "песочный"},
    {"цветочный", "цветок", "весенний"},
    {"деревянный", "дуб", "берёза"},
    {"деревенский", "садовый"},
    {"смайлик", "счастливый"},
]

adjectives = [
    # colors
    {"word": "синий", "color": "#004DFF"},
    {"word": "красный", "color": "#FF0000"},
    {"word": "оранжевый", "color": "#FF8000"},
    {"word": "зелёный", "color": "#00FF00"},
    {"word": "серый", "color": "#858585"},
    {"word": "жёлтый", "color": "#FFFF00"},
    {"word": "розовый", "color": "#FFCBDB"},
    {"word": "аквамариновый", "color": "#7FFFD4"},
    {"word": "лиловый", "color": "#DB7093"},
    {"word": "алый", "color": "#FF2400"},
    {"word": "салатовый", "color": "#99ff99"},
    {"word": "голубой", "color": "#00BFFF"},
    {"word": "пурпурный", "color": "#C400AB"},
    {"word": "серебряный", "color": "#C0C0C0"},
    {"word": "золотой", "color": "#FFD700"},
    {"word": "фиолетовый", "color": "#5A009D"},
    {"word": "белый", "color": "#FFFFFF"},
    {"word": "сиреневый", "color": "#c8a2c8"},
    {"word": "малиновый", "color": "#dc143c"},
    # materials
    {"word": "деревянный"},
    {"word": "железный"},
    {"word": "ледяной"},
    {"word": "молочный"},
    {"word": "песочный"},
    {"word": "радостный"},
    {"word": "снежный"},
    {"word": "махровый"},
    {"word": "пушистый"},
    {"word": "шершавый"},
    {"word": "металлический"},
    {"word": "платиновый"},
    {"word": "хромированный"},
    # properties
    {"word": "холодный"},
    {"word": "тёплый"},
    {"word": "солнечный"},
    {"word": "ветренный"},
    {"word": "весенний"},
    {"word": "небесный", "color": "#87ceeb"},
    {"word": "морской", "color": "#00ffff"},
    {"word": "кофейный"},
    {"word": "цветочный"},
    {"word": "зимний"},
    {"word": "травяной"},
    {"word": "офисный"},
    {"word": "городской"},
    {"word": "стеклянный"},
    # no
    {"word": "цветной"},
    {"word": "ходячий"},
    {"word": "огненный"},
    {"word": "шумный"},
    {"word": "тихий"},
    {"word": "рабочий"},
    {"word": "заводской"},
    {"word": "уютный"},
    {"word": "деревенский"},
    {"word": "ресторанный"},
    {"word": "модный"},
    {"word": "дорогой"},
    {"word": "садовый"},
]

all_backgrounds = []
all_images = []
fonts = []

NOUNS_PATH = os.path.join(SCRIPT_PATH, "random_sources", "Существительные")
ADJS_PATH = os.path.join(SCRIPT_PATH, "random_sources", "Прилагательные")

if not os.path.exists(os.path.dirname(NOUNS_PATH)):
    os.makedirs(os.path.dirname(NOUNS_PATH))
if not os.path.exists(os.path.dirname(ADJS_PATH)):
    os.makedirs(os.path.dirname(ADJS_PATH))

images_directory = ""


def find_word_description(descriptions_list, word):
    for description in descriptions_list:
        if description["word"] == word:
            return description
    return None


def download_one(address, path):
    print("Download: %s -> %s", address, path)
    r = requests.get(address, allow_redirects=True)
    open(path, "wb").write(r.content)


def download_images(dir_path):
    for noun in nouns:
        word = noun["word"]
        word_directory_path = dir_path + word + "/"
        print("%s:" % (word_directory_path))
        if os.path.exists(word_directory_path):
            continue

        os.makedirs(word_directory_path)

        enWord = translator.translate(word, src="ru", dest="en").text
        print("%s - %s" % (word, enWord))
        counter = 0
        for page_num in range(max_pages):
            r = requests.get(
                "https://www.stickpng.com/search?q=%s&page=%d"
                % (urllib.parse.quote(enWord), page_num + 1)
            )
            tree = html.fromstring(r.text)
            found = False

            for element in tree.xpath('//a[@class = "image pattern"]'):
                ref = element.get("href")
                image_page_request = requests.get("https://www.stickpng.com%s" % (ref))
                image_page = html.fromstring(image_page_request.text)
                for image_element in image_page.xpath(
                    '//div[@class = "image"]/img[@src]'
                ):
                    executor.submit(
                        download_one,
                        image_element.get("src"),
                        "%s%d.png" % (word_directory_path, counter),
                    )
                    counter += 1
                    found = True

            if not found:
                break


def get_form(morph, form):
    morph_form = morph.inflect(form)
    if morph_form:
        return morph_form.word
    else:
        return morph.word


def find_pos(array, POS):
    for element in array:
        if element.tag.POS == POS:
            return element
    return array[0]


def prepare_words():
    global nouns, adjectives

    # Nouns

    for word_description in nouns:
        word = word_description["word"]
        morph_source = find_pos(morph.parse(word), "NOUN")
        word_description["morph"] = morph_source

        images_path = os.path.join("random_sources", "Существительные", word)
        if os.path.exists(images_path):
            images_list = []
            for obj in os.listdir(images_path):
                obj_path = os.path.join(images_path, obj)
                images_list.append(obj_path)
                all_images.append(obj_path)

            if len(images_list) != 0:
                word_description["images"] = images_list
        """
        sing_gent = morph_source.inflect({'sing', 'gent'})
        if sing_gent:
            sing_gent = sing_gent.word
        else:
            sing_gent = word
        word_description['sing_gent'] = sing_gent

        plur_gent = morph_source.inflect({'plur', 'gent'})
        if plur_gent:
            plur_gent = plur_gent.word
        else:
            plur_gent = sing_gent

        word_description['sing_gent'] = sing_gent
        word_description['plur_gent'] = plur_gent
        """

    # Adjectives
    for word_description in adjectives:
        word = word_description["word"]
        morph_source = find_pos(morph.parse(word), "ADJF")
        word_description["morph"] = morph_source

        texture_path = os.path.join("random_sources", "Текстуры", word)
        if os.path.exists(texture_path):
            textures_list = []
            for obj in os.listdir(texture_path):
                obj_path = os.path.join(texture_path, obj)
                textures_list.append(obj_path)
                all_backgrounds.append(obj_path)

            if len(textures_list) != 0:
                word_description["textures"] = textures_list

        background_path = os.path.join("random_sources", "Фоны", word)
        if os.path.exists(background_path):
            backgrounds_list = []

            for obj in os.listdir(background_path):
                obj_path = os.path.join(background_path, obj)
                backgrounds_list.append(obj_path)
                all_backgrounds.append(obj_path)

            if len(backgrounds_list) != 0:
                word_description["backgrounds"] = backgrounds_list

    random_path = os.path.join("random_sources", "Фоны", "random")
    for obj in os.listdir(random_path):
        obj_path = os.path.join(random_path, obj)
        all_backgrounds.append(obj_path)

    fonts_path = os.path.join("random_sources", "Шрифты")
    for font in os.listdir(fonts_path):
        font_path = os.path.join(fonts_path, font)
        fonts.append(ImageFont.truetype(font_path, 74))


def gen_main_forms(noun_description):
    global adjectives
    adj_description = random.choice(adjectives)

    noun_normal = noun_description["morph"]
    noun_form_params = set()
    if not (("Sgtm" in noun_normal.tag) or ("Pltm" in noun_normal.tag)):
        number = random.randint(0, 1)
        if number == 0:
            noun_form_params.add("sing")
        elif number == 1:
            noun_form_params.add("plur")
    noun_form_params.add("gent")

    noun_form = noun_normal.inflect(noun_form_params) or noun_normal

    adj_form_params = set()
    if noun_form.tag.number:
        adj_form_params.add(noun_form.tag.number)
        if noun_form.tag.number == "sing":
            if noun_form.tag.gender:
                adj_form_params.add(noun_form.tag.gender)
    adj_form_params.add("gent")

    adj_normal = adj_description["morph"]
    adj_form = adj_normal.inflect(adj_form_params) or adj_normal

    return adj_description, noun_form, adj_form


# Main program

prepare_words()

adjective_object_property_tags = {"color", "textures"}


def get_existing_tags(description, tags):
    result = []
    for tag in tags:
        if tag in description:
            result.append(tag)
    return result


def get_object_property_tags_set(adjective_description):
    global adjective_object_property_tags
    return get_existing_tags(adjective_description, adjective_object_property_tags)


background_tags = {"textures", "backgrounds"}


def get_random_background(adjective_description):
    # random theme
    existing_tags = background_tags.intersection(adjective_description)

    if (len(existing_tags) == 0) or (random.random() < 0.4):
        return random.choice(all_backgrounds)
    else:
        if len(existing_tags) == 1:
            return random.choice(list(adjective_description[list(existing_tags)[0]]))
        else:
            if random.random() < 30:
                return random.choice(adjective_description["textures"])
            else:
                return random.choice(adjective_description["backgrounds"])


def get_need_scale(image_size, box_size):
    return min(box_size[0] / image_size[0], box_size[1] / image_size[1])


IMAGE_SIZE = (1024, 1024)
MAX_NOUN_IMAGE_SIZE = (800, 800)  # scale = 1
MIN_NOUN_IMAGE_SIZE = (128, 128)  # scale = MIN_SCALE
MIN_SCALE = get_need_scale(MAX_NOUN_IMAGE_SIZE, MIN_NOUN_IMAGE_SIZE)

watermark_paths = [
    os.path.join(SCRIPT_PATH, "random_sources", "watermark_1.png"),
    os.path.join(SCRIPT_PATH, "random_sources", "watermark_2.png"),
]

watermark_images = []
for watermark_path in watermark_paths:
    watermark_image = Image.open(watermark_path).convert("RGBA")
    watermark_size = (int(649 / 849 * 1024), int(163 / 849 * 1024))
    watermark_image = watermark_image.resize(watermark_size)
    watermark_images.append(watermark_image)


def interpolate(x1, x2, percent):
    return x1 + (x2 - x1) * percent


def get_random_scale(big_object=False):
    if big_object:
        return (
            interpolate(640, MAX_NOUN_IMAGE_SIZE[0], random.random())
            / MAX_NOUN_IMAGE_SIZE[0]
        )
    else:
        rand = random.random()
        if rand < 0.1:
            return (
                interpolate(MIN_NOUN_IMAGE_SIZE[0], 196, random.random())
                / MAX_NOUN_IMAGE_SIZE[0]
            )
        elif rand < 0.8:
            return interpolate(196, 420, random.random()) / MAX_NOUN_IMAGE_SIZE[0]
        else:
            return (
                interpolate(420, MAX_NOUN_IMAGE_SIZE[0], random.random())
                / MAX_NOUN_IMAGE_SIZE[0]
            )


def inc_matrix(pos, size, bg_size, matrix):
    columns = len(matrix[0])
    rows = len(matrix)

    cell_width = bg_size[0] / columns
    cell_height = bg_size[1] / rows

    for x in range(
        max(math.floor(pos[0] / cell_width), 0),
        min(math.floor((pos[0] + size[0]) / cell_width), columns - 1) + 1,
    ):
        for y in range(
            max(math.floor(pos[1] / cell_height), 0),
            min(math.floor((pos[1] + size[1]) / cell_height), rows - 1) + 1,
        ):
            matrix[y][x] += 1


def draw_text_with_stroke(
    draw, pos, text, font, fill_color, stroke_color=(0, 0, 0, 255), stroke_width=0
):
    x = pos[0]
    y = pos[1]
    for offset in range(stroke_width):
        offset += 1
        # thin border
        draw.text((x - offset, y), text, font=font, fill=stroke_color)
        draw.text((x + offset, y), text, font=font, fill=stroke_color)
        draw.text((x, y - offset), text, font=font, fill=stroke_color)
        draw.text((x, y + offset), text, font=font, fill=stroke_color)

        # thicker border
        draw.text((x - offset, y - offset), text, font=font, fill=stroke_color)
        draw.text((x + offset, y - offset), text, font=font, fill=stroke_color)
        draw.text((x - offset, y + offset), text, font=font, fill=stroke_color)
        draw.text((x + offset, y + offset), text, font=font, fill=stroke_color)

    draw.text((x, y), text, font=font, fill=fill_color)


def hex_to_rgb(rgb):
    h = rgb.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def get_normalized(color):
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)


def get_base255(color, alpha=None):
    return (int(color[0] * 255.0), int(color[1] * 255.0), int(color[2] * 255.0))


def get_stroke_color(color):
    hls = colorsys.rgb_to_hls(*get_normalized(color))
    if hls[1] < 0.5:
        return (255, 255, 255, 255)
    else:
        return (0, 0, 0, 255)


def change_image_color(image, color):
    dest_color = numpy.array(color) / 255.0
    dest_color_hsv = matplotlib.colors.rgb_to_hsv(dest_color)

    image_rgba = numpy.asarray(image) / 255.0
    image_hsv = matplotlib.colors.rgb_to_hsv(image_rgba[:, :, 0:3])
    image_v = image_hsv[:, :, 2]

    result_m_rgb = numpy.zeros((image_rgba.shape[0], image_rgba.shape[1], 3))
    result_m_rgb[:, :] = numpy.array(color) / 255.0
    result_m_rgb[:, :] *= image_v[:, :, numpy.newaxis] ** 1.7

    result_h_hsv = numpy.copy(image_hsv)
    result_h_hsv[:, :, 0] = dest_color_hsv[0]
    result_h_rgb = matplotlib.colors.hsv_to_rgb(result_h_hsv)

    sat = dest_color_hsv[1]

    result_rgb = result_h_rgb * sat + result_m_rgb * (1.0 - sat)
    result_rgba = numpy.dstack((result_rgb, image_rgba[:, :, 3]))

    return Image.fromarray((result_rgba * 255.0).astype(numpy.uint8))


def bind_texture(image, texture):
    resized_texture = texture.resize(image.size)
    image_rgba = numpy.asarray(image) / 255.0
    texture_rgba = numpy.asarray(resized_texture) / 255.0
    image_hsv = matplotlib.colors.rgb_to_hsv(image_rgba[:, :, 0:3])
    image_v = image_hsv[:, :, 2]

    # + image_rgba[:, :, 0:3] * (1.0 - image_v)
    result_rgb = numpy.multiply(texture_rgba[:, :, 0:3], image_v[:, :, numpy.newaxis])
    result_rgba = numpy.dstack((result_rgb, image_rgba[:, :, 3]))

    return Image.fromarray((result_rgba * 255.0).astype(numpy.uint8))


adjective_tags = {"textures", "backgrounds", "color"}
adjective_tags_weights = {
    "textures": 2,
    "color": 6,
    "backgrounds": 2,
}


def gen_postcard(noun_description):

    # --------------------------------Choice noun-----------------------------

    adjective_description, noun_form, adj_form = gen_main_forms(noun_description)

    # --------------------------------------------------------------------------
    # --------------------------------Draw image------------------------------
    # --------------------------------------------------------------------------

    # Select counts
    noun_images_count = random.randint(2, 5)
    if noun_images_count < 4:
        random_images_count = random.randint(2, 5)
    else:
        random_images_count = random.randint(1, 4)

    # Choice images
    noun_images = []
    random_images = []

    if "images" in noun_description:
        images_list = noun_description["images"]
        for counter in range(noun_images_count):
            noun_images.append(random.choice(images_list))
    else:
        random_images_count += noun_images_count

    for counter in range(random_images_count):
        random_images.append(random.choice(all_images))

    # 50% get adjective theme background
    background_image_path = get_random_background(adjective_description)
    # print(text)
    # print(background_image_path)
    background_image = Image.open(background_image_path).convert("RGBA")

    crop_left = 0
    crop_right = background_image.size[0]
    crop_top = 0
    crop_bottom = background_image.size[1]
    if background_image.size[0] < background_image.size[1]:
        crop_top = (background_image.size[1] - background_image.size[0]) // 2
        crop_bottom = crop_top + background_image.size[0]
    else:
        crop_left = (background_image.size[0] - background_image.size[1]) // 2
        crop_right = crop_left + background_image.size[1]

    background_image = background_image.crop(
        (crop_left, crop_top, crop_right, crop_bottom)
    )
    background_image = background_image.resize(IMAGE_SIZE)

    draw_images = []
    draw_images.extend(random_images)
    draw_images.extend(noun_images)
    random.shuffle(draw_images)

    if len(noun_images) != 0:
        big_boss = random.choice(noun_images)
    else:
        big_boss = random.choice(random_images)

    matrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    adj_tags = list(adjective_tags.intersection(adjective_description))
    adj_tags_weights = []
    for tag in adj_tags:
        adj_tags_weights.append(adjective_tags_weights[tag])

    for image_path in draw_images:
        image = Image.open(image_path).convert("RGBA")
        base_scale = get_need_scale(image.size, MAX_NOUN_IMAGE_SIZE)
        is_big_object = image_path == big_boss
        scale = base_scale * get_random_scale(is_big_object)
        resized_image = image.resize(
            (int(image.size[0] * scale), int(image.size[1] * scale))
        )

        if (image_path in noun_images) and (len(adj_tags) != 0):
            if random.random() < 0.9:
                selected_tag = random.choices(adj_tags, weights=adj_tags_weights, k=1)[
                    0
                ]
                if selected_tag == "textures":
                    selected_texture = Image.open(
                        random.choice(adjective_description["textures"])
                    ).convert("RGBA")
                elif selected_tag == "backgrounds":
                    selected_texture = Image.open(
                        random.choice(adjective_description["backgrounds"])
                    ).convert("RGBA")

                if selected_tag == "color":
                    resized_image = change_image_color(
                        resized_image, hex_to_rgb(adjective_description["color"])
                    )
                elif selected_texture is not None:
                    resized_image = bind_texture(resized_image, selected_texture)

        pos_x = int(
            interpolate(
                0, background_image.size[0] - resized_image.size[0], random.random()
            )
        )
        pos_y = int(
            interpolate(
                0, background_image.size[1] - resized_image.size[1], random.random()
            )
        )
        background_image.paste(resized_image, (pos_x, pos_y), mask=resized_image)
        inc_matrix(
            (pos_x, pos_y),
            resized_image.size,
            (
                background_image.size[0],
                background_image.size[1] - WATERMARK_BOTTOM_OFFSET,
            ),
            matrix,
        )

    # Render text

    font = random.choice(fonts)
    if random.random() < 0.1:
        render_line_1 = "Со всемирным днём "
        render_line_2 = "%s %s!" % (adj_form.word, noun_form.word)
    elif random.random() < 0.2:
        render_line_1 = "С международным днём "
        render_line_2 = "%s %s!" % (adj_form.word, noun_form.word)
    elif random.random() < 0.3:
        render_line_1 = "Со всероссийским днём "
        render_line_2 = "%s %s!" % (adj_form.word, noun_form.word)
    else:
        render_line_1 = "С днём %s " % (adj_form.word)
        render_line_2 = "%s!" % (noun_form.word)

    render_one_line_text = render_line_1 + render_line_2

    render_line_1_size = font.getsize(render_line_1)
    render_line_2_size = font.getsize(render_line_2)
    render_one_line_text_size = font.getsize(render_one_line_text)

    # Select cells to draw
    min_sum = -1
    min_sum_indices = []
    min_sum_row_index = 0
    for row_index in range(len(matrix)):
        current_sum = 0
        for cell in matrix[row_index]:
            current_sum += cell
        if min_sum == -1 or min_sum > current_sum:
            min_sum_indices = []
            min_sum_indices.append(row_index)
            min_sum = current_sum
        elif min_sum == current_sum:
            min_sum_indices.append(row_index)

    min_sum_row_index = random.choice(min_sum_indices)

    cell_width = background_image.size[0] / len(matrix[0])
    cell_height = (background_image.size[1] - WATERMARK_BOTTOM_OFFSET) / len(matrix)
    max_text_width = interpolate(cell_width * 3, cell_width * 4, random.random())

    # Draw text

    draw = ImageDraw.Draw(background_image)
    all_text_offset_y = min_sum_row_index * cell_height

    if render_one_line_text_size[0] <= max_text_width:
        font_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            255,
        )

        draw_text_with_stroke(
            draw,
            (
                interpolate(
                    0,
                    background_image.size[0] - render_one_line_text_size[0],
                    random.random(),
                ),
                all_text_offset_y + (cell_height - render_one_line_text_size[1]) / 2,
            ),
            render_one_line_text,
            font=font,
            fill_color=font_color,
            stroke_width=2,
            stroke_color=get_stroke_color(font_color),
        )

    else:
        text_width = max(render_line_1_size[0], render_line_2_size[0])
        text_x = interpolate(0, background_image.size[0] - text_width, random.random())

        text_height = render_line_1_size[1] + render_line_2_size[1]
        text_y = (cell_height - text_height) / 2
        font_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            255,
        )
        draw_text_with_stroke(
            draw,
            (text_x, all_text_offset_y + text_y),
            render_line_1,
            font=font,
            fill_color=font_color,
            stroke_width=2,
            stroke_color=get_stroke_color(font_color),
        )

        font_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            255,
        )
        draw_text_with_stroke(
            draw,
            (
                text_x + (text_width - render_line_2_size[0]) / 2,
                all_text_offset_y + text_y + render_line_1_size[1] + 10,
            ),
            render_line_2,
            font=font,
            fill_color=font_color,
            stroke_width=2,
            stroke_color=get_stroke_color(font_color),
        )

    result = []
    for watermark_image in watermark_images:
        result_image = background_image.copy()
        result_image.paste(
            watermark_image,
            (
                (background_image.size[0] - watermark_image.size[0]) // 2,
                background_image.size[1] - watermark_image.size[1],
            ),
            mask=watermark_image,
        )
        result.append(result_image.convert("RGB"))

    return result


def gen_random():
    return gen_postcard(random.choice(nouns))


class TestTestAnswer:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text

    def get_name(self):
        return self.text


async def handle_answers(answers, test):
    global nouns

    key_number = 143297  # Pseudo random result select key
    module = len(nouns) * 59

    # Find for known nomns and compute answers hash
    result_number = zlib.crc32(bytes(test.get_name(), "utf-8")) % module
    known_nouns = []
    for answer in answers:
        text = answer.get_text()
        words = re.findall(r"\w+", text)
        for word in words:
            word_morph = find_pos(morph.parse(word), "NOUN")
            if not word_morph:
                continue

            form_attribs = {"nomn"}

            if (not ("Pltm" in word_morph.tag)) and (not ("Sgtm" in word_morph.tag)):
                form_attribs.add("sing")
            word_normal = word_morph.inflect(form_attribs)
            if not word_normal:
                continue

            description = find_word_description(nouns, word_normal.word)
            if description:
                known_nouns.append(description)

        textHash = zlib.crc32(bytes(text, "utf-8")) % module
        result_number = (result_number + textHash) % module

    result_number = (result_number + (key_number % module)) % module

    # --------------------------------Choice noun-----------------------------

    # 80%, that noun will be const
    if random.random() < 0.8:
        random.seed(result_number)

        if known_nouns:
            noun_description = random.choice(known_nouns)
        else:
            noun_description = random.choice(nouns)

        # Return true random
        random.seed()
    else:
        noun_description = random.choice(nouns)

    image = gen_postcard(noun_description)
    return "", None, image


# Отладка
import time


def main():
    global nouns_path, nouns

    result = 0
    for i in range(100):
        millis1 = int(round(time.time() * 1000))
        img = gen_random()
        millis2 = int(round(time.time() * 1000))
        result += millis2 - millis1

    print(result / 100)
    img[0].show()
    return
    """
    #print(morph.parse('смайлик')[0])

    image = Image.open('random_sources/Существительные/апельсин/0.png')
        .convert("RGBA").resize( (256, 256) )
    image = change_image_color(image, hex_to_rgb('#ffffff'))
    image.show()
    return

    image = Image.open('random_sources/Существительные/апельсин/0.png')
        .convert("RGBA").resize( (256, 256) )
    texture = Image.open(
        'random_sources/Текстуры/кофейный/1ab34c62f20e67b0d558ff55e3488d57.jpg'
        ).convert("RGBA").resize( (256, 256) )
    image = bind_texture(image, texture)
    image.show()
    return

    answers = [
        TestTestAnswer('возможно'),
        TestTestAnswer('спагетти'),
        TestTestAnswer('кролик'),
        TestTestAnswer('рот'),
        TestTestAnswer('самолет'),
        TestTestAnswer('Я убираю ихних звёзд, делаю чистым небо'),
        TestTestAnswer('42'),
    ]
    #for counter in range(100):
    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(
            handle_answers(answers, TestTestAnswer('Какая ты открытка'))
        )
        result[2].show()
    finally:
        #loop.run_until_complete(
        #   handle_answers(answers, TestTestAnswer('Какая ты открытка'))
        # )
        loop.close()
    """


if __name__ == "__main__":
    main()
