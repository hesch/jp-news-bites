import feedparser
import requests


def download_latest_podcast(audio_url, output_path):
    # Download the audio file
    audio_data = requests.get(audio_url)
    # Save the audio file locally
    with open(output_path, "wb") as audio_file:
        audio_file.write(audio_data.content)


def get_basic_info(rss_feed_url):
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)
    # Get the first entry (latest podcast episode)
    latest_episode = feed.entries[0]
    return {
        'audio_url': latest_episode.media_content[0]['url'],
        'link': latest_episode.link,
        'title': latest_episode.title,
        'slug': latest_episode.link.split("/")[-1],
    }
