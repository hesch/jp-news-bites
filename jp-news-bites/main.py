from pydub import AudioSegment
import os
import openai
import json
import pickle
import config
import rss
import audio
import transcript
import podlove


def main():
    conf = config.Config("config.json")

    openai.api_key = conf.openai_api_key

    basic_info = rss.get_basic_info(conf.rss_feed_url)
    # Modify output dir so we have a unique location for every episode
    conf.output_dir = os.path.join(conf.output_dir, basic_info["slug"])
    if os.path.exists(conf.output_dir):
        print(f"path already exists: {conf.output_dir}\nSkipping...")
        return 1
    os.makedirs(conf.output_dir, exist_ok=True)
    # Download the latest podcast
    print(basic_info)
    # input("Press Enter to continue...")
    audio_file_path = os.path.join(conf.output_dir, "latest_podcast.mp3")
    if os.path.isfile(audio_file_path):
        print(f"{audio_file_path} exists")
        print("Skipping download")
    else:
        rss.download_latest_podcast(basic_info["audio_url"], audio_file_path)
        print(f"Downloaded latest podcast: {audio_file_path}")

    # Extract the first 10 minutes
    segment_path = audio.extract_first_10_minutes(conf, audio_file_path)
    print(f"Extracted first 10 minutes: {segment_path}")

    segment_path = os.path.join(conf.output_dir, "first_10_minutes.mp3")
    # Transcribe the first 10 minutes
    transcript_path = segment_path + ".trans"
    if os.path.isfile(transcript_path):
        print(f"{transcript_path} exists")
        print("Skipping transcribe")
        with open(transcript_path, "rb") as transcript_file:
            transcription_data = pickle.load(transcript_file)
    else:
        transcription_data = transcript.transcribe_audio_clip(segment_path)
        with open(transcript_path, "wb") as transcript_file:
            pickle.dump(transcription_data, transcript_file)

    json_path = os.path.join(conf.output_dir, "json_segments.json")
    if os.path.isfile(json_path):
        print(f"{json_path} exists")
        print("Skipping segment classification")
        with open(json_path, "r", encoding="utf-8") as file:
            stories = json.load(file)
    else:
        json_data = transcript.classify_segments(transcription_data)
        with open(json_path, "w", encoding="utf-8") as file:
            file.write(json_data)
        stories = json.loads(json_data)

    audio_seg = AudioSegment.from_mp3(segment_path)
    episodes = audio.segment_audio(
        conf,
        audio_seg,
        transcription_data.segments,
        stories,
        basic_info["slug"]
    )
    # input("verify result")
    file_paths = [e[key] for e in episodes for key in [
        "audio_path", "transcript_path"] if key in e]
    podlove.upload_media_files(conf, file_paths)

    for episode in episodes:
        podlove.create_episode_wp(
            conf, basic_info["title"], basic_info["link"], episode)


if __name__ == "__main__":
    main()
