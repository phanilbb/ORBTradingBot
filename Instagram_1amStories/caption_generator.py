import random

import hashtag_generator

CAPTION = """{caption}
.
Tag someone ❤️
.
.
{hashtags}
.
"""


def generate_caption(content):
    hashtags = hashtag_generator.generate_hashtags_from_text(content['Content'], content['Category'])
    caption = CAPTION.format(caption=content['Caption'], hashtags=hashtags)

    return caption
