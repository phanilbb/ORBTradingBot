import os
import random
import textwrap
import time
import PIL.Image
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from helpers import constants
import s3

LOGO_TEXT = '@1am.storiess'


def get_images(topic):
    images_data = s3.get_images_list(topic)
    if not images_data:
        images_data = s3.get_images_list("default")
    file_path = random.choice(images_data)
    local_file_path = s3.download_file(file_path, '/tmp', "downloaded_image.jpg")
    return Image.open(local_file_path)


def add_logo_text(image, text, text_color):
    fontsize = constants.LOGO_FONT_SIZE
    font = ImageFont.truetype(constants.LOGO_FONT_LOCATION, fontsize)
    new_text = textwrap.fill(text=text, replace_whitespace=False, max_lines=8)
    draw = ImageDraw.Draw(image)

    # Calculate text size and position
    text_width, text_height = draw.textsize(new_text, font)
    x = (image.width - text_width) // 2  # Center horizontally
    y = image.height - text_height - 20  # Bottom of the image

    draw.text((x, y), text=new_text, font=font, fill=text_color, align='center')

    return image


def add_main_text(image, text, text_color, text_width=constants.TEXT_WIDTH_POST):
    fontsize = constants.TEXT_FONT_SIZE
    font = ImageFont.truetype(constants.TEXT_FONT_LOCATION, fontsize)

    draw = ImageDraw.Draw(image)

    title_height, content_height = 0, 0
    titles, contents = [], []
    if 'Title' in text:
        title = textwrap.fill(text=text['Title'], replace_whitespace=False, width=text_width)
        title_width, title_height = draw.textsize(title, font)
        titles = textwrap.wrap(text=text['Title'], replace_whitespace=False, width=text_width)

    if 'Content' in text:
        content = textwrap.fill(text=text['Content'], replace_whitespace=False, width=text_width)
        content_width, content_height = draw.textsize(content, font)
        contents = textwrap.wrap(text=text['Content'], replace_whitespace=False, width=text_width)

    line_spacing = constants.LINE_SPACING
    text_height = title_height + content_height + 14 * line_spacing

    y = (image.height - text_height) // 2

    each_line_height = 0

    if titles:
        for each_title in titles:
            for each_line in each_title.split('\n'):
                each_line_width, each_line_height = draw.textsize(each_line, font)
                x = (image.width - each_line_width) // 2
                draw.text((x, y), text=each_line, font=font, fill=text_color, spacing=line_spacing, stroke_width=3,
                          stroke_fill=(0, 0, 0, 80))
                y += (each_line_height + line_spacing)
        else:
            y += (each_line_height + line_spacing)

    if contents:
        for each_content in contents:
            for each_line in each_content.split('\n'):
                each_line_width, each_line_height = draw.textsize(each_line, font)
                x = (image.width - each_line_width) // 2
                draw.text((x, y), text=each_line, font=font, fill=text_color, spacing=line_spacing, stroke_width=3,
                          stroke_fill=(0, 0, 0, 80))
                y += (each_line_height + line_spacing)

    return image


def add_text(background, text):
    text_color = (255, 255, 255)
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.45)
    background = background.filter(ImageFilter.GaussianBlur(3))
    add_main_text(background, text, text_color)
    add_logo_text(background, LOGO_TEXT, text_color)
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
    im = Image.open(image_path)
    im.show()
    print("Image generated successfully")
    return image_paths


def make_image(content):
    image = get_images(content['Category'])
    return image_editor(image, "{}.jpg".format(str(round(time.time() * 1000))), content)
