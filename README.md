# JP News Bites

This is the script that automates https://learn-jp-news.com

The website is designed for learners of Japanese, that want to listen to small news stories and read along.
It uses the audio from 今週の気になるニュース and publishes the news articles as small audio snippets.

First whisper-1 is used to create a transcript of the first 10 minutes of the podcast.
Then ChatGPT is asked to classify the segments into the news stories.
Based on the classification, the audio is clipped and the transcript transformed into VTT format.
The media files are uploaded using SCP.
The last step is using the Podlove/Wordpress API to create posts for every news story.


# Technologies

- Feedparser lib: parse the RSS feed
- pydub + ffmpeg: cutting the audio clips
- whisper-1: creating the transcript
- ChatGPT: classify the transcript
- paramiko: Python SCP library
- Wordpress: host the blog
- Podlove: Wordpress plugin that provides the player

