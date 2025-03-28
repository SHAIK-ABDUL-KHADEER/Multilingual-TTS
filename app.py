from flask import Flask, request, render_template, send_from_directory, jsonify
from deep_translator import GoogleTranslator
import os
import hashlib
import asyncio
import edge_tts
from datetime import datetime

app = Flask(__name__)

# Set up paths and folders
OUTPUT_FOLDER = "static/tts_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Updated Supported Languages & Codes
LANGUAGES = {
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Punjabi": "pa-IN",
    "English": "en-US",
    "Assamese": "as-IN",
    "Odia": "or-IN",
    "Urdu": "ur-IN",
    "Sinhala": "si-LK",
    "Nepali": "ne-NP",
    "Arabic": "ar-SA",
    "French": "fr-FR",
    "German": "de-DE",
    "Spanish": "es-ES",
}

# ✅ Updated Voices for Each Language
VOICES = {
    "Hindi": {"Male": "hi-IN-MadhurNeural", "Female": "hi-IN-SwaraNeural"},
    "Bengali": {"Male": "bn-IN-TanmayNeural", "Female": "bn-IN-TushitaNeural"},
    "Telugu": {"Male": "te-IN-MohanNeural", "Female": "te-IN-ShrutiNeural"},
    "Tamil": {"Male": "ta-IN-ValluvarNeural", "Female": "ta-IN-PallaviNeural"},
    "Marathi": {"Male": "mr-IN-ManoharNeural", "Female": "mr-IN-AarohiNeural"},
    "Gujarati": {"Male": "gu-IN-NiranjanNeural", "Female": "gu-IN-DhwaniNeural"},
    "Kannada": {"Male": "kn-IN-GaganNeural", "Female": "kn-IN-SapnaNeural"},
    "Malayalam": {"Male": "ml-IN-MidhunNeural", "Female": "ml-IN-SobhanaNeural"},
    "Punjabi": {"Male": "pa-IN-BaljeetNeural", "Female": "pa-IN-NeerjaNeural"},
    "English": {"Male": "en-US-GuyNeural", "Female": "en-US-JennyNeural"},
    "Assamese": {"Male": "as-IN-KartikNeural", "Female": "as-IN-MadhuriNeural"},
    "Odia": {"Male": "or-IN-SatyajitNeural", "Female": "or-IN-PragyaNeural"},
    "Urdu": {"Male": "ur-IN-SalmanNeural", "Female": "ur-IN-SalmaNeural"},
    "Sinhala": {"Male": "si-LK-SameeraNeural", "Female": "si-LK-NirashaNeural"},
    "Nepali": {"Male": "ne-NP-RameshNeural", "Female": "ne-NP-SaritaNeural"},
    "Arabic": {"Male": "ar-SA-FarisNeural", "Female": "ar-SA-ZaynabNeural"},
    "French": {"Male": "fr-FR-HenriNeural", "Female": "fr-FR-DeniseNeural"},
    "German": {"Male": "de-DE-ConradNeural", "Female": "de-DE-KatjaNeural"},
    "Spanish": {"Male": "es-ES-AlvaroNeural", "Female": "es-ES-ElviraNeural"},
}


# ✅ Generate and save Edge TTS audio
async def generate_edge_tts(text, voice, output_path):
    communicate = edge_tts.Communicate(text=text, voice=voice)
    try:
        await communicate.save(output_path)
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise


@app.route("/", methods=["GET", "POST"])
def index():
    audio_files = get_audio_files()

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        language = request.form.get("language")
        gender = request.form.get("gender")

        if not text:
            return render_template(
                "index.html",
                error="Please enter some text.",
                audio_files=audio_files,
                LANGUAGES=LANGUAGES,
                language=language,
                gender=gender,
            )

        try:
            # Translate text
            target_lang_code = LANGUAGES[language].split('-')[0]
            translated_text = GoogleTranslator(source='auto', target=target_lang_code).translate(text)

            # Generate unique hash for file
            safe_hash = hashlib.md5(f"{text}_{language}_{gender}".encode()).hexdigest()
            output_path = f"{OUTPUT_FOLDER}/tts_{safe_hash}.mp3"

            # Check if file already exists (cache)
            if not os.path.exists(output_path):
                voice = VOICES[language][gender]
                asyncio.run(generate_edge_tts(translated_text, voice, output_path))

            audio_files = get_audio_files()
            return render_template(
                "index.html",
                text=text,
                translated_text=translated_text,
                audio_url=f"/audio/tts_{safe_hash}.mp3",
                audio_files=audio_files,
                LANGUAGES=LANGUAGES,
                language=language,  # Retain language after submission
                gender=gender,      # Retain gender after submission
            )

        except Exception as e:
            return render_template(
                "index.html",
                error=f"Error: {str(e)}",
                audio_files=audio_files,
                LANGUAGES=LANGUAGES,
                language=language,
                gender=gender,
            )

    # Initial load with default values
    return render_template(
        "index.html",
        audio_files=audio_files,
        LANGUAGES=LANGUAGES,
        language="Hindi",  # Default to Hindi
        gender="Female"    # Default to Female
    )


# ✅ Get audio files
def get_audio_files():
    """Fetch all audio files in the /tts_output folder."""
    files = []
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".mp3"):
            file_path = f"/audio/{filename}"
            creation_time = datetime.fromtimestamp(
                os.path.getctime(os.path.join(OUTPUT_FOLDER, filename))
            ).strftime("%Y-%m-%d %H:%M:%S")
            files.append({"name": filename, "url": file_path, "time": creation_time})

    # Sort files by creation time (newest first)
    files.sort(key=lambda x: x["time"], reverse=True)
    return files


# ✅ Serve generated audio
@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
