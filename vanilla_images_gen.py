from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import os.path
import random
from PIL import Image, ImageDraw
from PIL import ImageFont
import random_picture
import math
import colorsys
import time


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
MODELS_DIR = os.path.join(SCRIPT_PATH, "models", "vanilla_phrases")
models_paths = [
    os.path.join(MODELS_DIR, "vanilla_phrases_gen_v2.2"),
    os.path.join(MODELS_DIR, "vanilla_phrases_gen_v2.2.2"),
    os.path.join(MODELS_DIR, "vanilla_phrases_gen_model_last"),
    os.path.join(MODELS_DIR, "vanilla_phrases_gen_model_first"),
]

TRAIN_TEXT_PATH = os.path.join(MODELS_DIR, "vanilla_phrases_gen_v2.2")

TRAIN_TEXT_FILE_PATH = os.path.join(MODELS_DIR, "train_text.txt")

with open(TRAIN_TEXT_FILE_PATH, encoding="utf-8") as text_file:
    text_sample = text_file.readlines()
text_sample = " ".join(text_sample)


def text_to_seq(text_sample):
    char_counts = Counter(text_sample)
    char_counts = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)

    sorted_chars = [char for char, _ in char_counts]
    char_to_idx = {char: index for index, char in enumerate(sorted_chars)}
    idx_to_char = {v: k for k, v in char_to_idx.items()}
    sequence = np.array([char_to_idx[char] for char in text_sample])

    return sequence, char_to_idx, idx_to_char


sequence, char_to_idx, idx_to_char = text_to_seq(text_sample)

SEQ_LEN = 256
BATCH_SIZE = 16


def get_batch(sequence):
    trains = []
    targets = []
    for _ in range(BATCH_SIZE):
        batch_start = np.random.randint(0, len(sequence) - SEQ_LEN)
        chunk = sequence[batch_start : batch_start + SEQ_LEN]
        train = torch.LongTensor(chunk[:-1]).view(-1, 1)
        target = torch.LongTensor(chunk[1:]).view(-1, 1)
        trains.append(train)
        targets.append(target)
    return torch.stack(trains, dim=0), torch.stack(targets, dim=0)


def evaluate(
    model, char_to_idx, idx_to_char, start_text=" ", prediction_len=200, temp=0.3
):
    hidden = model.init_hidden()
    idx_input = [char_to_idx[char] for char in start_text]
    train = torch.LongTensor(idx_input).view(-1, 1, 1).to(device)
    predicted_text = start_text

    _, hidden = model(train, hidden)

    inp = train[-1].view(-1, 1, 1)

    for i in range(prediction_len):
        output, hidden = model(inp.to(device), hidden)
        output_logits = output.cpu().data.view(-1)
        p_next = F.softmax(output_logits / temp, dim=-1).detach().cpu().data.numpy()
        top_index = np.random.choice(len(char_to_idx), p=p_next)
        inp = torch.LongTensor([top_index]).view(-1, 1, 1).to(device)
        predicted_char = idx_to_char[top_index]
        predicted_text += predicted_char

    return predicted_text


class TextRNN(nn.Module):
    def __init__(self, input_size, hidden_size, embedding_size, n_layers=1):
        super(TextRNN, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.embedding_size = embedding_size
        self.n_layers = n_layers

        self.encoder = nn.Embedding(self.input_size, self.embedding_size)
        self.lstm = nn.LSTM(self.embedding_size, self.hidden_size, self.n_layers)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(self.hidden_size, self.input_size)

    def forward(self, x, hidden):
        x = self.encoder(x).squeeze(2)
        out, (ht1, ct1) = self.lstm(x, hidden)
        out = self.dropout(out)
        x = self.fc(out)
        return x, (ht1, ct1)

    def init_hidden(self, batch_size=1):
        return (
            torch.zeros(
                self.n_layers, batch_size, self.hidden_size, requires_grad=True
            ).to(device),
            torch.zeros(
                self.n_layers, batch_size, self.hidden_size, requires_grad=True
            ).to(device),
        )


device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

models = []

for model_path in models_paths:
    model = TextRNN(
        input_size=len(idx_to_char), hidden_size=128, embedding_size=128, n_layers=2
    )
    model.to(device)

    model.load_state_dict(torch.load(models_paths[1]))

    model.eval()

    models.append(model)

divisors = ".…!?"


def gen_phrase():
    generated = evaluate(
        random.choice(models),
        char_to_idx,
        idx_to_char,
        temp=0.3,
        prediction_len=500,
        start_text=". ",
    )

    generated = generated.lstrip()

    positions = []
    for index in range(len(generated)):
        if generated[index] in divisors:
            positions.append(index)

    max_sentences_count = min(2, len(positions) - 1)
    if max_sentences_count > 1:
        sentences_count = random.randint(1, max_sentences_count)
    else:
        return generated.lstrip()

    start_position = random.randint(0, len(positions) - sentences_count - 1)
    stop_position = start_position + sentences_count

    while True:

        selected_phrase = generated[
            positions[start_position] + 1 : positions[stop_position] + 1
        ].lstrip()
        if len(selected_phrase) < 5:
            can_expand_back = start_position > 0
            can_expand_front = stop_position < len(positions) - 1

            if can_expand_front:
                stop_position += 1
            elif can_expand_back:
                start_position -= 1
            else:
                return generated.lstrip()
        else:
            return selected_phrase


SOURCES_PATH = os.path.join(SCRIPT_PATH, "vanilla_phrases_sources")

IMAGES_PATH = os.path.join(SOURCES_PATH, "images")

FONTS_PATH = os.path.join(SOURCES_PATH, "fonts")
WATERMARK_PATHS = [
    os.path.join(SOURCES_PATH, "watermarks", "watermark_1.png"),
    os.path.join(SOURCES_PATH, "watermarks", "watermark_2.png"),
]


def pixels_to_points(pixels):
    return pixels * 72 / 96


def points_to_pixels(points):
    return points * 96 / 72


font_pixels_cahce_sizes = [25, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200]
fonts = []
images = []
watermark_images = []


def init():
    for obj in os.listdir(IMAGES_PATH):
        obj_path = os.path.join(IMAGES_PATH, obj)
        images.append(obj_path)

    for font in os.listdir(FONTS_PATH):
        font_path = os.path.join(FONTS_PATH, font)
        font_cache = []
        for pixels_size in font_pixels_cahce_sizes:
            font_cache.append(
                ImageFont.truetype(font_path, int(pixels_to_points(pixels_size)))
            )
        fonts.append(font_cache)

    for watermark_path in WATERMARK_PATHS:
        watermark_image = Image.open(watermark_path).convert("RGBA")
        watermark_size = (int(649 / 849 * 1024), int(163 / 849 * 1024))
        watermark_image = watermark_image.resize(watermark_size)
        watermark_images.append(watermark_image)


RANDOM_FONT_L_BOTTOM_LIM = 0.25


def get_font_color(bg_image):
    image = np.array(bg_image)

    avg_color_per_row = np.average(image, axis=0)
    avg_colors = np.average(avg_color_per_row, axis=0)

    hls = colorsys.rgb_to_hls(*random_picture.get_normalized(avg_colors))

    result_h = hls[0] + 0.5
    result_h = result_h - math.floor(result_h)
    if hls[1] < RANDOM_FONT_L_BOTTOM_LIM:
        result_l = random.uniform(RANDOM_FONT_L_BOTTOM_LIM, 1.0)
    else:
        result_l = random.uniform(0.0, RANDOM_FONT_L_BOTTOM_LIM)

    result_hls = (result_h, result_l, random.random())

    result_rgb = random_picture.get_base255(colorsys.hls_to_rgb(*result_hls))
    return (
        result_rgb[0],
        result_rgb[1],
        result_rgb[2],
        255,
    )


def get_stroke_color(color):
    hls = colorsys.rgb_to_hls(*random_picture.get_normalized(color))
    if hls[1] < 0.25:
        return (255, 255, 255, 255)
    else:
        return (0, 0, 0, 255)


init()

AVAILABLE_FONT_HEIGHT_PERCENT = 0.85
AVAILABLE_FONT_WIDTH_PERCENT = 0.75

AVAILABLE_FONT_AREA_PERCENT = (
    AVAILABLE_FONT_WIDTH_PERCENT * AVAILABLE_FONT_HEIGHT_PERCENT
)
AVAILABLE_AREA_FACTOR = 0.85

WATERMARK_HEIGHT_PERCENT = 0.1919


def gen_image():
    image_path = random.choice(images)
    # image_path = r"C:\Users\Nick\Documents\Orders\Mail.ru\ICQTests\ICQPostcardsService\vanilla_phrases_sources\images\Pink-flowers-background-garden_1920x1200.jpg"
    image = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    while True:
        try:
            text = gen_phrase()
            break
        except:
            pass
    # text = "И стремление к ней. Платон Кто не отпущенный всегда ищет соответствующую ему половину."
    font_list = random.choice(fonts)

    font = font_list[-1]
    text_size = draw.textsize(text, font)
    text_area = text_size[0] * text_size[1]

    available_area = (
        image.size[0]
        * image.size[1]
        * AVAILABLE_FONT_AREA_PERCENT
        * AVAILABLE_AREA_FACTOR
    )

    if available_area < text_area:
        multiplier = math.sqrt(available_area / text_area)
        required_size = font_pixels_cahce_sizes[-1] * multiplier

        for index in range(len(font_pixels_cahce_sizes) - 1, -1, -1):
            font = font_list[index]
            if font_pixels_cahce_sizes[index] < required_size:
                break

    available_width = image.size[0] * AVAILABLE_FONT_WIDTH_PERCENT
    lines = []
    current_line_start_pos = 0
    while True:
        try:
            current_line_end = text.index(" ", current_line_start_pos)
        except:
            lines.append(text[current_line_start_pos:])
            break

        current_line = text[current_line_start_pos:current_line_end]
        current_line_width = draw.textsize(current_line, font)[0]
        while True:
            try:
                new_line_end = text.index(" ", current_line_end + 1)
            except:
                new_line_end = len(text)

            new_line = text[current_line_start_pos:new_line_end]
            new_line_width = draw.textsize(new_line, font)[0]

            if new_line_width < available_width:
                current_line_end = new_line_end
                current_line = new_line
                current_line_width = new_line_width

                if new_line_end == len(text):
                    break
            else:
                break

        lines.append(current_line)
        current_line_start_pos = current_line_end + 1
        if current_line_start_pos >= len(text):
            break

    text_height = 0
    for line in lines:
        text_height += draw.textsize(line, font)[1]

    text_offset_y = (image.size[1] - text_height) // 2

    font_color = get_font_color(image)

    line_offset_y = text_offset_y
    for line in lines:
        line_size = draw.textsize(line, font)

        random_picture.draw_text_with_stroke(
            draw,
            ((image.size[0] - line_size[0]) // 2, line_offset_y),
            line,
            font=font,
            fill_color=font_color,
            stroke_width=2,
            stroke_color=get_stroke_color(font_color),
        )
        line_offset_y += line_size[1]

    result = []

    watermark_height = int(image.size[1] * WATERMARK_HEIGHT_PERCENT)

    for watermark_image in watermark_images:
        max_width = int(
            min(
                watermark_height / watermark_image.size[1] * watermark_image.size[0],
                image.size[0],
            )
        )

        watermark_image = watermark_image.resize(
            (
                max_width,
                int(max_width / watermark_image.size[0] * watermark_image.size[1]),
            )
        )
        result_image = image.copy()

        result_image.paste(
            watermark_image,
            (
                (image.size[0] - watermark_image.size[0]) // 2,
                image.size[1] - watermark_image.size[1],
            ),
            mask=watermark_image,
        )
        result.append(result_image.convert("RGB"))
    return result


if __name__ == "__main__":
    for i in range(20):
        gen_image()[0].show()
