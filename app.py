from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
import feedparser
import hashlib
from datetime import datetime, timedelta, date
import time, random
import logging
import csv
import os


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
    print(len(items))
    # Filter items within the last year and not chosen before
    recent_items = [
        item for item in items
        if get_published_date(item) and datetime.fromtimestamp(time.mktime(get_published_date(item))) > datetime.now() - timedelta(days=365)
    ]

    print(len(recent_items))
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

@app.route('/rate', methods=['POST'])
def rate_feed():
    print(request.form)
    rating = int(request.form['rating'])

    feed_url = request.form['feed_url']

    save_to_csv(feed_url, rating)

    return 'Thank you for rating the quote!'

def save_to_csv(feed_url, rating):
    today = date.today().strftime("%Y-%m-%d")

    # Check if the date already exists in the CSV file
    with open('content_ratings.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)
        for row in rows:
            if row and row[0] == today:
                row[1] = feed_url  # Update the quote
                row[2] = rating  # Update the rating
                break
        else:
            # If the date does not exist, append a new row
            rows.append([today, feed_url, rating])

    # Write all the rows back to the CSV file
    with open('content_ratings.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def get_image_filenames():
    image_dir = os.path.join(app.static_folder, 'jpg')
    if os.path.exists(image_dir):
        return sorted(os.listdir(image_dir))
    else:
        return []


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
        print(today_seed)
        # Get a random item from the chosen feed using the seed
        random_item = get_random_item(random_feed, today_seed)
        # print(random_item)
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
    images = get_image_filenames()
    return render_template(
        'display_content.html',
        content=random_item.title,
        link=random_item.link,
        encouragement_phrase=encouragement_phrase,
        feed_link=random_feed,
        images=images,
    )

if __name__ == '__main__':
    app.run(debug=True)
