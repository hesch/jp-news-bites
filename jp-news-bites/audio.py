import os
import logging
from pydub import AudioSegment
from transcript import transcript_output

log = logging.getLogger(__name__)


def extract_first_10_minutes(config, audio_file_path):
    audio = AudioSegment.from_mp3(audio_file_path)
    ten_minutes_ms = 10 * 60 * 1000
    first_ten_minutes = audio[:ten_minutes_ms]
    file_path = os.path.join(config.output_dir, "first_10_minutes.mp3")
    first_ten_minutes.export(file_path, format="mp3")
    return file_path


def segment_audio(config, audio, segment_data, story_data, slug):
    episodes = []
    stories = story_data["news_stories"]
    for i, story in enumerate(stories):
        start_time = segment_data[story["start_index"]]["start"] * 1000
        end_time = segment_data[story["end_index"]]["end"] * 1000
        clip = audio[start_time:end_time]

        # Define the output file paths
        base_output_file_path = f"{config.output_dir}/{slug}_{i+1}"
        audio_output_file_path = f"{base_output_file_path}.mp3"
        transcript_output_file_path = f"{base_output_file_path}_transcript.vtt"

        # Export the clip
        clip.export(audio_output_file_path, format="mp3")
        log.info(f"Saved clip: {audio_output_file_path}")

        # Export the transcript
        transcript = transcript_output(
            segment_data, story["start_index"], story["end_index"])
        with open(transcript_output_file_path, "w") as tf:
            tf.write(transcript)
        log.info(f"Saved transcript: {transcript_output_file_path}")
        episodes.append({
            "title": story["title"],
            "number": i,
            "duration": end_time-start_time,
            "audio_path": audio_output_file_path,
            "transcript_path": transcript_output_file_path,
        })

    return episodes
