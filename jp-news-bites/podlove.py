import os
import logging
import requests
from requests.auth import HTTPBasicAuth
import paramiko
import transcript

log = logging.getLogger(__name__)


def upload_media_files(conf, paths):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_key = paramiko.RSAKey.from_private_key_file(
            conf.media_server.ssh_key_path
        )

        # Connect to the server
        ssh.connect(
            conf.media_server.host,
            port=conf.media_server.port,
            username=conf.media_server.user,
            pkey=ssh_key
        )

        # Open an SFTP session
        sftp = ssh.open_sftp()
        for path in paths:
            # Upload the file
            file_name = os.path.basename(path)
            sftp.put(path, conf.media_server.remote_dir + file_name)
            log.info(f"Successfully uploaded {path} to {
                conf.media_server.remote_dir}")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()
    except Exception as e:
        log.error(f"Failed to upload file: {e}")
        log.error("Exception occurred:")
        log.error("Type:", type(e))
        log.error("Arguments:", e.args)
        log.error("Exception message:", str(e))
        raise e


def create_episode_wp(conf, original_title, original_link, episode):
    endpoint = "/wp-json/podlove/v2/episodes"

    # General params for the connection
    headers = {
        'Content-Type': 'application/json'
    }

    auth = HTTPBasicAuth(conf.podlove.user, conf.podlove.password)

    # Create episode draft
    response = requests.post(conf.podlove.url + endpoint,
                             headers=headers, auth=auth)

    if response.status_code == 201:
        log.info("Episode created successfully!")
    else:
        log.error(f"Failed to create episode: {response.status_code}")
        log.debug(response.json())
        return

    episode_id = response.json()["id"]

    media_filename = os.path.basename(episode["audio_path"])
    episode_data = {
        "title": episode["title"],
        "subtitle": f"{original_title} 第{episode['number']}番のニュース",
        "summary": f"""
This is news story number {episode['number']+1} from the podcast 今週の気になるニュース by 田村淳.
If you like the story and would like to listen to the discussion following the news stories, please go to the original episode.
You can find it here: <a href="{original_link}">{original_link}</a>
        """,
        "type": "full",  # full, trailer or bonus
        "slug": os.path.splitext(media_filename)[0],
        # Duration in HH:MM:SS
        "duration": transcript.format_milliseconds_for_webvtt(episode["duration"], include_ms=True),
    }

    # Populate the episode with data
    response = requests.put(f"{conf.podlove.url}{
                            endpoint}/{episode_id}", json=episode_data, headers=headers, auth=auth)
    if response.status_code == 200:
        log.info("Episode data set!")
    else:
        log.error(f"Failed set episode data: {response.status_code}")
        log.debug(response.json())
        return

    # Get the episode to find the wordpress post id
    response = requests.get(f"{conf.podlove.url}{
                            endpoint}/{episode_id}", auth=auth)
    if response.status_code != 200:
        log.error(f"Failed to get episode id: {response.status_code}")
        log.debug(response.json())
        return
    wp_episode_id = response.json()["post_id"]

    post_endpoint = "/wp-json/wp/v2/episodes"
    response = requests.get(
        f"{conf.podlove.url}{post_endpoint}/{wp_episode_id}",
        headers=headers,
        auth=auth
    )

    post_content = response.json()["content"]
    post_content["rendered"] += episode_data["summary"]
    # Publish the episode
    response = requests.post(
        f"{conf.podlove.url}{post_endpoint}/{wp_episode_id}",
        json={
            "status": "publish",
            "content": post_content,
        },
        headers=headers,
        auth=auth
    )
    if response.status_code == 200:
        log.info("Episode published successfully!")
    else:
        log.error(f"Failed to publish episode: {response.status_code}")
        log.debug(response.json())
        return

    return response
