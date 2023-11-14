import hashtag_generator

CAPTION = """Like if you relate. Share if you love.
.
.
#LifeInEveryMoment
#1amStories
.
.
—————————————————
{hashtags}
.
{author}
"""


def generate_caption(text, topic, author):
    if not author or author == '-':
        author = '.'
    else:
        author = 'By - ' + author

    hashtags = hashtag_generator.generate_hashtags_from_text(text, topic)

    caption = CAPTION.format(hashtags=hashtags, author=author)

    return caption
