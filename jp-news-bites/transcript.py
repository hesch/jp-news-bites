import openai


def transcribe_audio_clip(clip_path):
    # Load the audio file
    with open(clip_path, "rb") as audio_file:
        # Transcribe the audio using ChatGPT API
        response = openai.audio.transcriptions.create(
            model="whisper-1",  # or another model name
            language="ja",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )
    return response


def transcript_to_str(t):
    out = ""
    for idx, seg in enumerate(t.segments):
        out += f"{idx}: {seg['text']}\n"
    return out


def classify_segments(transcript):
    transcript_string = transcript_to_str(transcript)
    print(transcript_string)
    system_message = """
You are a language model tasked with analyzing podcast transcripts in Japanese.
Your goal is to identify the start and end segments of each news story within the transcript.
In the first sentence of the stories the name of the newspaper is mentioned.
The start index should point to the segment that mentions the name of the newspaper.
After the last news story there will be a sentence like "以上、今週のニュースをお届けしました".
For each news story, you need to provide the following information in JSON format:

1. News Story Title: A brief title or description of the news story.
2. Start Index: The index number in the transcript where the news story begins.
3. End Index: The index number in the transcript where the news story ends.

Please output the result in a structured JSON format with an array of objects, each representing a news story segment.

Example format:
[
  {
    "title": "News Story 1 Title",
    "start_index": Start Index,
    "end_index": End Index
  },
  {
    "title": "News Story 2 Title",
    "start_index": Start Index,
    "end_index": End Index
  },
  ...
]
"""

    # Make the API call
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # or the appropriate model
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": transcript_string}
        ],
        max_tokens=1000,  # Adjust as needed
        temperature=0.5,  # Control the randomness
        response_format={"type": "json_object"}
    )

    # Extract the JSON output
    return response.choices[0].message.content


def format_milliseconds_for_webvtt(timestamp_ms, include_ms=True):
    # Extract hours, minutes, seconds, and milliseconds
    milliseconds = int(timestamp_ms % 1000)
    seconds = int((timestamp_ms // 1000) % 60)
    minutes = int((timestamp_ms // (1000 * 60)) % 60)
    hours = int((timestamp_ms // (1000 * 60 * 60)) % 24)

    # Format the time string with leading zeros
    if include_ms:
        formatted_time = f"{hours:02}:{minutes:02}:{
            seconds:02}.{milliseconds:03}"
    else:
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    return formatted_time


def transcript_output(segment_data, start_index, end_index):
    clip_start = segment_data[start_index]["start"]
    output = "WEBVTT\n\n"
    for i, seg in enumerate(segment_data[start_index:end_index+1]):
        time_start = format_milliseconds_for_webvtt(
            int((seg['start']-clip_start)*1000)+1)
        time_end = format_milliseconds_for_webvtt(
            int((seg['end']-clip_start)*1000))
        output += f"{time_start} --> {time_end}\n<v 砂ちゃん>{seg['text']}\n\n"
    return output
