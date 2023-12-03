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
—————————————————
{tags}
"""

TAGS = [
    'healer1463',
    'barlage6969',
    'melissa.rose06',
    'diordiorlitty',
    'sarah.m_777',
    'nadia_rose_19',
    'st_acy2641',
    'preciousphrincess',
    'esraa.7537',
    'az6rii',
    'beautifulm101',
    'abbydewitt12',
    'sensualselfexplorer',
    'vals_mundo.99',
    'shalonda_knutson',
    'bballkay28',
    'game_over_rg',
    'goldyglitter_collection'
]


def generate_caption(text, topic, author):
    if not author or author == '-' or author == '':
        author = '.'
    else:
        author = 'By - ' + author

    hashtags = hashtag_generator.generate_hashtags_from_text(text, topic)

    tags = ['@' + each for each in TAGS]

    caption = CAPTION.format(hashtags=hashtags, author=author, tags=' '.join(tags))

    return caption
