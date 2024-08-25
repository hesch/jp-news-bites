import json


class Podlove:
    def __init__(self, podlove):
        self.url = podlove["url"]
        self.user = podlove["user"]
        self.password = podlove["password"]


class MediaServer:
    def __init__(self, media):
        self.host = media["host"]
        self.port = media["port"]
        self.user = media["user"]
        self.remote_dir = media["remote_dir"]
        self.ssh_key_path = media["ssh_key_path"]


class Config:
    def __init__(self, config_path):
        with open(config_path) as config_file:
            config = json.load(config_file)
        self.output_dir = config["output_dir"]
        self.openai_api_key = config["openai_api_key"]
        self.rss_feed_url = config["rss_feed_url"]
        self.podlove = Podlove(config["podlove"])
        self.media_server = MediaServer(config["media_server"])
