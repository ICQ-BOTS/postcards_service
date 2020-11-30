import os
import os.path
from PIL import Image


for address, dirs, files in os.walk("vanilla_phrases_sources"):
    for file in files:
        if ".png" in file:
            image_format = "PNG"
        elif ".jpg" in file or ".jpeg" in file:
            image_format = "JPEG"
        else:
            continue

        file_path = os.path.join(address, file)

        print(f"Prepare: {file_path}")
        image = Image.open(file_path)
        aspect_ratio = image.size[0] / image.size[1]
        if image.size[0] > image.size[1]:
            image = image.resize((int(aspect_ratio * 1024), 1024))
        else:
            image = image.resize((1024, int(1024 / aspect_ratio)))
        image.save(file_path, image_format)
