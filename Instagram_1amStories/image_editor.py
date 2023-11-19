import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imgur
import requests
import background_selector


def get_images(topic):
    image_data = image_uploader.get_images_list(topic)
    index = background_selector.get_background_index(topic, len(image_data) - 1)
    file = image_data[index]
    return Image.open(requests.get(file['link'], stream=True).raw), '{}.jpg'.format(file['id'])


def add_bg_line(image, text, font, text_color, text_start_height):
    max_words_per_line = 8
    max_characters_per_line = 45
    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size
    y_text = text_start_height

    words = text.split()  # Split the text into individual words
    lines = []
    current_line = []

    for word in words:
        if len(current_line) + len(word.split()) <= max_words_per_line:
            if len(' '.join(current_line)) + len(word) <= max_characters_per_line:
                current_line.extend(word.split())
            else:
                lines.append(current_line)
                current_line = word.split()
        else:
            lines.append(current_line)
            current_line = word.split()

    # Append any remaining words as the last line
    if current_line:
        lines.append(current_line)

    for line in lines:
        line = ' '.join(line)
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y_text), line, font=font, fill=text_color, align='left')
        y_text += line_height

    return y_text


def add_bg_text(image, text, font, text_color):
    line_spacing = 10
    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size
    text_width, text_height = draw.textsize(text, font)

    y_text = (image_height - text_height) // 2 - (((image_height - text_height) // 2) / 100) * 30

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            y_text = add_bg_line(image, line, font, text_color, y_text)
            y_text += line_spacing
        else:
            y_text += 3 * line_spacing

    return image


def add_text(background, text):
    fontsize = 50
    font = ImageFont.truetype("Dosis-Bold.ttf", fontsize)
    text_color = (255, 255, 255)
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.45)
    add_bg_text(background, text, font, text_color)
    return background


def image_editor(background, background_name, text):
    tmp_dir = '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    image_paths = []
    background = add_text(background, text)
    image_path = os.path.join(tmp_dir, background_name)
    background.save(image_path)
    image_paths.append(image_path)
    # im = Image.open(image_path)
    # im.show()
    print("Image generated successfully")
    return image_paths


def make_image(content, topic):
    BACKGROUND, BACKGROUND_NAME = get_images(topic)
    return image_editor(BACKGROUND, BACKGROUND_NAME, content)
