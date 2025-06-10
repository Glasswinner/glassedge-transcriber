from flask import Flask, request, jsonify
import whisper
import requests
import subprocess
import os

app = Flask(__name__)
model = whisper.load_model("base")  # use "medium" if you upgrade RAM on Render

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    video_url = data.get("videoUrl")
    if not video_url:
        return jsonify({"error": "Missing videoUrl"}), 400

    try:
        # Download video from Cloudinary
        video_path = "temp.mp4"
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)

        # Convert to WAV using ffmpeg
        audio_path = "temp.wav"
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_path
        ], check=True)

        # Transcribe using Whisper
        result = model.transcribe(audio_path)
        return jsonify({
            "text": result["text"],
            "segments": result.get("segments", [])
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
