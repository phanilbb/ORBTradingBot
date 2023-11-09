import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

background_config = {
    'bg1.jpg': {
        'fontsize': 70,
        'text_start_height': 400,
        'enhancer': 0.3
    }
}


def get_images(start_directory):
    backgrounds = []
    backgrounds_name = []

    os.chdir('background')
    directory = os.listdir(os.curdir)

    for file in directory:
        backgrounds.append(Image.open(file))
        backgrounds_name.append(file)

    os.chdir(start_directory)

    return backgrounds, backgrounds_name


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
    line_spacing = 6
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
        draw.text((x_text, y_text), line, font=font, fill=text_color)
        y_text += text_height + line_spacing

    return image


def add_text(background, text, width, background_name):
    config = background_config[background_name]
    fontsize = config['fontsize']
    if '\n' in text:
        fontsize = 50
    font = ImageFont.truetype("Dosis-Bold.ttf", fontsize)

    text_color = (255, 255, 255)
    text_count = text.count('')
    text_count = text_count / 30
    text_start_height = config['text_start_height'] - (28 * text_count)

    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(config['enhancer'])

    if '\n' in text:
        add_bg_text_for_poem(background, text, font, text_color)
    else:
        add_bg_text_for_quote(background, text, font, text_color, text_start_height, width)
    return background


def image_editor(backgrounds, backgrounds_name, quote):
    random.shuffle(backgrounds)
    tmp_dir = '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    image_paths = []
    for background in backgrounds:
        background_name = backgrounds_name[backgrounds.index(background)]
        text = quote
        current_index = backgrounds.index(background)
        width, height = background.width - 40, background.height
        background = add_text(background, text, width, background_name)
        image_path = os.path.join(tmp_dir, background_name)
        background.save(image_path)
        image_paths.append(image_path)
        # im = Image.open(image_path)
        # im.show()
        print("Image generated successfully")

    return image_paths


def make_image(content, type):
    START_DIRECTORY = os.getcwd()
    BACKGROUNDS, BACKGROUNDS_NAME = get_images(START_DIRECTORY)
    return image_editor(BACKGROUNDS, BACKGROUNDS_NAME, content)


if __name__ == "__main__":
    content = '''In the journey of life, we'll find our way,
    Failure is the night before a brighter day.
    With courage and faith, we'll overcome the fall,
    Failure is the challenge that makes us stand tall.
    '''

    text = "Love is not about how much you say 'I love you,' but how much you can prove that it's true."
    print(make_image(content.strip(), 'love'))
