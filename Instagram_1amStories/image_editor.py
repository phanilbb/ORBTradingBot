import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import background_selector
import s3


def get_images(topic):
    images_data = s3.get_images_list(topic)
    index = background_selector.get_background_index(topic, len(images_data) - 1)
    file_path = images_data[index]
    local_file_path = s3.download_file(file_path, '/tmp', "downloaded_image.jpg")
    return Image.open(local_file_path)


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


def add_bg_text_2(image, text, font, text_color):
    new_text = textwrap.fill(text=text, replace_whitespace=False, max_lines=8)
    draw = ImageDraw.Draw(image)
    xy = (image.size[0] / 10, image.size[1] / 3)
    draw.text(xy, text=new_text, font=font, fill=text_color, align='center')
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
    image = get_images(topic)
    return image_editor(image, "downloaded_image.jpg", content)
