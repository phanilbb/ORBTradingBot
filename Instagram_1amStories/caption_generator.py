import random

import hashtag_generator

CAPTION = """{caption}
.
Tag someone ❤️
.
#LifeInEveryMoment
#1amStories
.
.
{hashtags}
.
.
{author}
"""

CAPTIONS = {

    "love": [
        "I expressed your love through a quote\nCan you express your love through a like? 🥰😁",
        "Love in every like 👍, and I'm loving you endlessly. ❤️👍",
        "If you heart this, you've just hearted my love story. Double-tap away! 💕",
        "A like for love, a love for a lifetime. Will you be my liker forever? 😊❤️",
        "Spread love, hit like. Let's turn this feed into a love fest! 🥰👍",
        "Clicking hearts because my heart belongs to you. Show some love with a like! 💖",
        "If love had a button, it would be the like button. Smash it for us! 💘👍",
        "Like if you believe in love at first sight. Our story started with a double-tap! 😍❤️",
        "Double tap and give me your heart ❤️. I will convey it to your partner on your behalf 🥰"
    ],
    "motivation": [
        "I motivated you through a quote\nCan u motivate me with a like? 🔥❤️",
        "Turning likes into motivation, one double-tap at a time. Give me a boost! 💪👍",
        "Your like is my fuel to keep the motivation burning. Let's light it up! 🔥❤️",
        "Need a dose of motivation? A like from you is the perfect remedy. Double-tap to inspire! 💙👍",
        "Each like is a step closer to achieving dreams. Help me climb the ladder of motivation! 🚀❤️",
        "Click that like button and be the spark in my motivational journey. Together, we rise! ⚡👍",
        "Motivation in exchange for a like – deal? Let's build a chain of positivity! 💫❤️",
        "Swipe up the motivation, double-tap to elevate. Are you ready for the climb? 🏔️👍",
        "A like today, motivation tomorrow. Join the journey of positive vibes! 🌈❤️",
        "Fueling my motivation, one like at a time. Ready to be part of the journey? 💪👍",
        "Like for motivation, share for inspiration. Let's create a ripple of positive energy! ✨❤️"
    ],
    "success": [
        "Double-tap for success vibes! Your like fuels the journey to triumph. 🌟👍",
        "Success is a mindset, and your like is the first step. Ready to conquer together? 💼❤️",
        "Click that like button and join the success squad. Let's elevate each other! 🚀👍",
        "Every like is a milestone on the road to success. Let's mark the path together! 🏆❤️",
        "Swipe right for success, double-tap for victory. Are you in for the win? 🏅👍",
        "Success starts with belief, and a like from you adds to the journey. Let's achieve! ✨❤️",
        "Like if you're on the path to success. Together, we'll create a legacy! 🌐👍",
        "A like today, success tomorrow. Join the ride to greatness! 🌈❤️",
        "Fueling my success, one like at a time. Please don't let me fail. 💪👍",
        "Success is sweet, but a like from you makes it sweeter. Let's savor the journey! 🍾❤️"
    ],
    "breakup": [
        "My Heart is broken 💔. Can you fix it with a like? ❤️",
        "Heartbroken but not defeated. A like is a step towards healing. 💔👍",
        "In the process of letting go, every like is a sigh of relief. Join me on the journey. 🌬️❤️",
        "Click like to send a virtual hug to my healing heart. Let's mend together. 🤗👍",
        "Swipe away the tears, double-tap for strength. Your support means the world. 💪❤️",
        "Broken but not shattered. Your like is a piece of my mending heart. 🧩👍",
        "If only likes could mend a broken heart. Let's find out together. 💔❤️",
        "Double-tap to say goodbye to the past and hello to a new beginning. 🌅👍",
        "Every like is a step towards self-love. Join me in the journey of healing. ❤️👍",
        "In the process of rewriting my story. Your like is a chapter in my healing book. 📖👍",
        "Like if you've been through heartbreak. We're stronger together. 💔❤️"
    ],
    "failure": [
        "Failure is not the end. It's a new beginning. Double-tap for resilience! 💪👍",
        "In the face of failure, every like is a step towards a comeback. Ready to rise? 🚀❤️",
        "Click like to join the journey of turning setbacks into comebacks. Let's conquer together! 🏹👍",
        "Every failure is a lesson, and your like is a reminder of strength. Learn, grow, repeat! 🌱❤️",
        "Swipe right for resilience, double-tap for a comeback. Are you in for the win? 🏆👍",
        "Failure is a detour, not a dead end. Like if you believe in the power of a comeback! 🔄❤️",
        "A like today, success tomorrow. Let's turn failure into fuel for greatness! 🔥👍",
        "Fueling my comeback, one like at a time. Pull me up with a like. 💪👍",
        "Like if you've faced failure and bounced back stronger. We're on this journey together! 💙❤️",
        "Failure is temporary; the comeback is permanent. Click like to be part of the success story! 🌟👍"
    ],
    "default": [
        "Like 👍 if you relate",
        "Double tap and see the magic 💙",
        "Like for love, share and share that love ❤️"
    ]

}


def generate_caption(text, topic, author):
    if not author or author == '-' or author == '':
        author = '.'
    else:
        author = 'By - ' + author

    hashtags = hashtag_generator.generate_hashtags_from_text(text, topic)

    captions = CAPTIONS.get(topic.lower())
    if not captions:
        captions = CAPTIONS.get("default")

    random.shuffle(captions)
    caption = captions[0]

    caption = CAPTION.format(caption=caption, hashtags=hashtags, author=author)

    return caption
