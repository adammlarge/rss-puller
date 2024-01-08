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
    'https://feeds.feedburner.com/TheCreativePenn',
    'https://feeds.feedburner.com/TheWritePractice',
    # Add more feeds as needed
]

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

    return chosen_item

@app.route('/')
def display_content():
    # Choose a random feed
    random_feed = random.choice(rss_feeds)

    # Generate a seed based on the current date
    today_seed = hashlib.sha256(str(datetime.utcnow().date()).encode()).hexdigest()

    # Get a random item from the chosen feed using the seed
    random_item = get_random_item(random_feed, today_seed)

    if not random_item:
        return "No eligible content available."

    return render_template('display_content.html', content=random_item.title, link=random_item.link)

if __name__ == '__main__':
    app.run(debug=True)
