import os
import subprocess
import wave
import contextlib
import datetime
import numpy as np
import json
from sklearn.cluster import AgglomerativeClustering
from whisper import load_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pyannote.audio import Audio
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.core import Segment
from django.views.decorators.csrf import csrf_exempt

# Define the folder where JSON files will be saved
TRANSCRIPT_FOLDER = "transcripts/"
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
whisper_model = load_model("base")
embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb")
audio = Audio()

def convert_to_wav(path):
    """
    Convert non-WAV audio to WAV format using ffmpeg.
    """
    if not path.endswith('.wav'):
        wav_path = f"{os.path.splitext(path)[0]}.wav"
        subprocess.call(['ffmpeg', '-i', path, wav_path, '-y'])
        return wav_path
    return path

def extract_embeddings(path, segments, duration):
    """
    Extract speaker embeddings for each audio segment.
    """
    embeddings = np.zeros((len(segments), 192))
    for i, segment in enumerate(segments):
        start = segment["start"]
        end = min(duration, segment["end"])
        clip = Segment(start, end)
        waveform, _ = audio.crop(path, clip)
        embeddings[i] = embedding_model(waveform[None])
    return np.nan_to_num(embeddings)

def perform_clustering(embeddings, num_speakers):
    """
    Perform clustering to identify speakers.
    """
    clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
    return clustering.labels_

def diarize_and_transcribe_audio(path, num_speakers=2):
    """
    Perform speaker diarization and transcription on the audio file.
    """
    wav_path = convert_to_wav(path)
    with contextlib.closing(wave.open(wav_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    result = whisper_model.transcribe(wav_path)
    segments = result["segments"]

    embeddings = extract_embeddings(wav_path, segments, duration)
    labels = perform_clustering(embeddings, num_speakers)
    for i in range(len(segments)):
        segments[i]["speaker"] = f"SPEAKER {labels[i] + 1}"

    transcript = []
    for segment in segments:
        transcript.append({
            "speaker": segment["speaker"],
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })

    return transcript

@csrf_exempt
def process_audio(request):
    """
    Django view to handle audio diarization and transcription.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method. Use POST.")

    if 'file' not in request.FILES:
        return HttpResponseBadRequest("No file provided.")

    uploaded_file = request.FILES['file']
    file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))

    try:
        transcript = diarize_and_transcribe_audio(file_path)

        file_name = os.path.splitext(uploaded_file.name)[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file_path = os.path.join(TRANSCRIPT_FOLDER, f"{file_name}_{timestamp}.json")
        
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump({"transcript": transcript}, json_file, ensure_ascii=False, indent=4)

        return JsonResponse({"transcript": transcript, "file_saved": json_file_path}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)



