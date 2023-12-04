import hashtag_generator

CAPTION = """Like if you relate. Share if you love. Follow for more.
.
.
#LifeInEveryMoment
#1amStories
—————————————————
{hashtags}
—————————————————
{author}
—————————————————
"""

TAGS = [
]


def generate_caption(text, topic, author):
    if not author or author == '-' or author == '':
        author = '.'
    else:
        author = 'By - ' + author

    hashtags = hashtag_generator.generate_hashtags_from_text(text, topic)

    tags = ['@' + each for each in TAGS]

    caption = CAPTION.format(hashtags=hashtags, author=author)

    return caption
