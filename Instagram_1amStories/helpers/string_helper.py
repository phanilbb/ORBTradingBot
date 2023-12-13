import re


def remove_prefix(original_string: str, prefix: str):
    if original_string.startswith(prefix):
        original_string = original_string[1:]
    return original_string


def remove_suffix(original_string: str, suffix: str):
    if original_string.endswith(suffix):
        original_string = original_string[:-1]
    return original_string


def remove_prefix_and_suffix(original_string: str, remove_str: str):
    original_string = remove_prefix(original_string, remove_str)
    original_string = remove_suffix(original_string, remove_str)
    return original_string


def add_prefix(original_string: str, prefix: str):
    if not original_string.startswith(prefix):
        original_string = prefix + original_string
    return original_string


def add_suffix(original_string: str, suffix: str):
    if not original_string.endswith(suffix):
        original_string = original_string + suffix
    return original_string


def add_prefix_and_suffix(original_string: str, add_str: str):
    original_string = add_prefix(original_string, add_str)
    original_string = add_suffix(original_string, add_str)
    return original_string


def split_string_by_emoji(input_string):
    s = []
    st = ''
    for each_char in input_string:
        if is_emoji(each_char):
            if st:
                s.append(st)
            s.append(each_char)
            st = ''
        else:
            st = st + each_char
    if st:
        s.append(st)
    return s


def is_emoji(s):
    # Define a Unicode range for common emojis
    # Define Unicode ranges for different emoji categories
    emoticons = (0x1F600, 0x1F64F)  # Emoticons
    symbols = (0x1F300, 0x1F5FF)  # Misc Symbols and Pictographs
    transport = (0x1F680, 0x1F6FF)  # Transport & Map Symbols
    alphanumeric = (0x1F700, 0x1F77F)  # Alphanumeric Supplement
    geometric = (0x1F780, 0x1F7FF)  # Geometric Shapes Extended
    mahjong = (0x1F000, 0x1F02F)  # Mahjong Tiles
    hearts = [(0x2764, 0x2764), (0x1F496, 0x1F496)]  # Heart emojis
    lightning = (0x26A1, 0x26A1)  # Lightning emoji
    happiness = (0x1F601, 0x1F604)  # Happiness emojis
    uncertainty = (0x1F615, 0x1F61A)  # Uncertainty emojis
    sadness = (0x1F61E, 0x1F622)  # Sadness emojis
    fear = (0x1F628, 0x1F632)  # Fear emojis
    love = (0x1F60D, 0x1F618)  # Love emojis
    supernatural = (0x1F47B, 0x1F47D)  # Supernatural emojis
    expressions = (0x1F604, 0x1F61F)  # Expressions emojis
    gestures = (0x1F464, 0x1F466)  # Gestures emojis
    people = (0x1F468, 0x1F469)  # People emojis
    animals = (0x1F431, 0x1F435)  # Animals face emojis
    food = (0x1F344, 0x1F347)  # Food & drink emojis
    flowers = (0x1F338, 0x1F33C)  # Flowers emojis
    travel = (0x1F30D, 0x1F30F)  # Travel & places emojis
    sports = (0x1F3C0, 0x1F3C4)  # Sports & activities emojis
    diwali = (0x1F9E6, 0x1F9E6)  # Diwali emoji

    emoji_ranges = [
        emoticons, symbols, transport, alphanumeric,
        geometric, mahjong, *hearts, lightning,
        happiness, uncertainty, sadness, fear, love,
        supernatural, expressions, gestures, people,
        animals, food, flowers, travel, sports, diwali
    ]

    # Check if any character in the string falls within the emoji Unicode ranges
    return any(any(emoji_range[0] <= ord(char) <= emoji_range[1] for emoji_range in emoji_ranges) for char in s)
