import speech_recognition as sr
import os
from pytubefix import YouTube
import subprocess

def download_youtube_audio(video_url, output_file="audio.wav"):
    print(f"Downloading video from {video_url}...")
    yt = YouTube(video_url)
    stream = yt.streams.filter(only_audio=True).first()
    downloaded_file = stream.download(filename="downloaded_audio")

    print("Converting video to WAV audio...")
    command = f"ffmpeg -i \"{downloaded_file}\" -vn -ar 16000 -ac 1 -f wav \"{output_file}\""
    subprocess.run(command, shell=True)

    os.remove(downloaded_file)
    print(f"Audio extracted and saved as {output_file}")
    return output_file

def transcribe_audio_file(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        print("Processing audio file...")
        audio_data = recognizer.record(source)

    try:
        print("Transcribing audio...")
        text = recognizer.recognize_google(audio_data, language='en-US')
        print("Transcription complete.")
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Error with the Google Speech Recognition service: {e}"

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=vlLZvNHeNbA"
    audio_file = download_youtube_audio(video_url, "youtube_audio.wav")

    transcription = transcribe_audio_file(audio_file)
    print("Transcribed Text:")
    print(transcription)

    # Optionally, save the transcription to a file
    # with open("transcription.txt", "w") as f:
    #    f.write(transcription)
