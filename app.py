from flask import Flask, render_template
from flask_basicauth import BasicAuth
import feedparser
import hashlib
from datetime import datetime, timedelta
import time, random

app = Flask(__name__)
basic_auth = BasicAuth(app)

# RSS Feeds
rss_feeds = [
    'https://thedutchphdcoach.com/feed/',
    'https://phdlife.warwick.ac.uk/feed/',
    'https://phdizone.com/feed/',
    'https://thesiswhisperer.com/feed/',
    'https://www.thedissertationcoach.com/feed/',
    'https://www.facultyfocus.com/feed/',
    'https://careerkarma.com/blog/feed/',
    'https://www.workitdaily.com/feeds/blog.rss',
    'https://theslowacademic.com/feed/',
    'https://phdinahundredsteps.com/feed/',
    'https://researchwhisperer.org/feed/',
    'https://phdwritingassistance.com/blog/index.php/feed/',
    'https://www.job-hunt.org/job-search-advice/feed/',
    'https://zenhabits.net/feed/',
    'https://every.to/superorganizers/feed.xml',
]


encouragement_phrases = [
    "You're making a difference.",
    "Keep pushing forward.",
    "Your efforts matter.",
    "Your potential is limitless.",
    "Success is within your reach.",
    "Your hard work will pay off.",
    "Stay positive and keep going.",
    "You're on the right track.",
    "Your resilience is inspiring.",
    "Every step is progress.",
    "You are enough.",
    "Keep going!",
    "I'm proud of what you've accomplished.",
    "There are always people rooting for you.",
    "Take care of yourself.",
]

chosen_items = set()
used_phrases = set()

# Memory to store chosen items
chosen_items = set()

def get_published_date(item):
    date_keys = ['published_parsed', 'pubDate', 'pub Date']

    for key in date_keys:
        if key in item:
            return item[key]

    return None

def get_random_item(feed_url, seed):
    feed = feedparser.parse(feed_url)
    items = feed.entries

    # Filter items within the last year and not chosen before
    recent_items = [
        item for item in items
        if get_published_date(item) and datetime.fromtimestamp(time.mktime(get_published_date(item))) > datetime.now() - timedelta(days=365)
        and item.link not in chosen_items
    ]


    if not recent_items:
        return None

    # Choose a random item using a deterministic seed
    random.seed(seed)
    chosen_item = random.choice(recent_items)
    chosen_items.add(chosen_item.link)
    print(chosen_item.title)
    print(chosen_item.link)
    return chosen_item

def get_random_encouragement_phrase():
    # Refill the list of used phrases if empty
    if not encouragement_phrases:
        encouragement_phrases.extend(used_phrases)
        used_phrases.clear()

    # Choose a random phrase
    chosen_phrase = random.choice(encouragement_phrases)
    encouragement_phrases.remove(chosen_phrase)
    used_phrases.add(chosen_phrase)

    return chosen_phrase

class Feed(object):

    def __init__(self,title="Sorry, something went wrong today"):
        self.title = "Sorry, something went wrong today"
        self.link = "https://www.pickthebrain.com/"

@app.route('/')
def display_content():
    rss_feeds = [
        'https://thedutchphdcoach.com/feed/',
        'https://phdlife.warwick.ac.uk/feed/',
        'https://phdizone.com/feed/',
        'https://thesiswhisperer.com/feed/',
        'https://www.thedissertationcoach.com/feed/',
        'https://www.facultyfocus.com/feed/',
        'https://careerkarma.com/blog/feed/',
        'https://www.workitdaily.com/feeds/blog.rss',
        'https://theslowacademic.com/feed/',
        'https://phdinahundredsteps.com/feed/',
        'https://researchwhisperer.org/feed/',
        'https://phdwritingassistance.com/blog/index.php/feed/',
        'https://www.job-hunt.org/job-search-advice/feed/',
        'https://zenhabits.net/feed/',
        'https://every.to/superorganizers/feed.xml',
    ]

    if rss_feeds:
        random_feed = random.choice(rss_feeds)
        
        print(random_feed)
        # Generate a seed based on the current date
        today_seed = hashlib.sha256(str(datetime.utcnow().date()).encode()).hexdigest()

        # Get a random item from the chosen feed using the seed
        random_item = get_random_item(random_feed, today_seed)
        
        todays_feeds=rss_feeds
        
        if not random_item:
            todays_feeds.remove(random_feed)
            while len(todays_feeds)>1:
                random_feed = random.choice(todays_feeds)
                todays_feeds.remove(random_feed)

            random_item = Feed()
    else:
        print('no feed')
        random_item = Feed(title="I can't find a new tip for today")

    encouragement_phrase = get_random_encouragement_phrase()

    return render_template('display_content.html', content=random_item.title, link=random_item.link,encouragement_phrase=encouragement_phrase)

if __name__ == '__main__':
    app.run(debug=True)
