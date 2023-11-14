import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import image_uploader
import requests
import background_selector


def get_images(topic):
    image_data = image_uploader.get_images_list(topic)
    index = background_selector.get_background_index(topic, len(image_data) - 1)
    file = image_data[index]
    return Image.open(requests.get(file['link'], stream=True).raw), '{}.jpg'.format(file['id'])


def add_bg_text_for_quote(image, text, font, text_color, text_start_height, width):
    max_words_per_line = 6
    max_characters_per_line = 36
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
        draw.text(((image_width - line_width) / 2, y_text), line, font=font, fill=text_color)
        y_text += line_height

    return image


def add_bg_text_for_poem(image, text, font, text_color):
    line_spacing = 10
    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size
    text_width, text_height = draw.textsize(text, font)

    x_text = (image_width - text_width) // 2
    y_text = (image_height - text_height) // 2 - (((image_height - text_height) // 2) / 100) * 30

    # Split the text into lines
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        text_width, text_height = draw.textsize(line, font)
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y_text), line, font=font, fill=text_color, align="center")
        y_text += (text_height + line_spacing)

    return image


def add_text(background, text, width):
    fontsize = 50
    font = ImageFont.truetype("Dosis-Bold.ttf", fontsize)

    text_color = (255, 255, 255)
    text_count = text.count('')
    text_count = text_count / 30
    text_start_height = 500 - (28 * text_count)

    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.45)

    if '\n' in text:
        add_bg_text_for_poem(background, text, font, text_color)
    else:
        add_bg_text_for_quote(background, text, font, text_color, text_start_height, width)
    return background


def image_editor(background, background_name, text):
    tmp_dir = '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    image_paths = []
    width, height = background.width - 40, background.height
    background = add_text(background, text, width)
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
