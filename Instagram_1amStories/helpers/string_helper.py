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
