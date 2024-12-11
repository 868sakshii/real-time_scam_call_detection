# import os
# import threading
# from src.audio_transcription import transcribe_audio
# from src.keyword_detection import KeywordDetector  # Corrected import path
# import time

# # Initialize Keyword Detector with your fine-tuned model
# detector = KeywordDetector(model_path="D:\scam-call-detection\saved_model", scam_threshold=0.4)  # Adjust path and threshold as needed

# def risk_assessment(transcription):
#     """
#     Assess the risk of a transcription using the KeywordDetector.
#     """
#     detection_result = detector.detect_keywords(transcription)
    
#     # Print risk assessment results
#     print(f"Transcription: {transcription}")
#     if detection_result["is_scam"]:
#         print(f"⚠ Scam Alert: Confidence {detection_result['confidence']:.2f}")
#     else:
#         print(f"✔ Safe: Confidence {detection_result['confidence']:.2f}")
    
#     # Return the risk result for further processing
#     return detection_result


# def main():
#     """
#     Main function to integrate the entire workflow.
#     """
#     print("Starting real-time scam call detection system...\n")
    
#     # Launch audio transcription in a separate thread
#     def audio_processing():
#         print("Listening for audio...")
#         transcribe_audio()
    
#     try:
#         # Run audio transcription (with language detection) and risk assessment
#         threading.Thread(target=audio_processing, daemon=True).start()
        
#         while True:
#             # Simulate waiting for transcriptions to process (replace with your logic)
#             time.sleep(5)  # Adjust based on your processing speed

#     except KeyboardInterrupt:
#         print("\nExiting the scam call detection system.")
#     except Exception as e:
#         print(f"Error in main workflow: {e}")
#     finally:
#         print("System cleanup completed. Exiting.")

# if __name__ == "_main_":
#     main()

import streamlit as st
import pyaudio
from vosk import Model, KaldiRecognizer
import json
import re
import logging
import os  # Import the os module
from src.keyword_detection import KeywordDetector  # Import the KeywordDetector class

# Path to the English Vosk model
MODEL_PATH = r"D:\scam-call-detection\models\vosk_model\vosk-model-small-en-in-0.4"

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

def load_model():
    """
    Load the Vosk model for English.
    """
    if not os.path.exists(MODEL_PATH):
        raise ValueError(f"Model path is invalid: {MODEL_PATH}")

    logging.info("Loading Vosk model for English.")
    return Model(MODEL_PATH)

def preprocess_text(text):
    """
    Preprocess the input text to clean unnecessary characters and normalize it.
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)  # Remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    return text

def transcribe_audio(callback=None):
    """
    Transcribe audio from the microphone.
    """
    model = load_model()
    recognizer = KaldiRecognizer(model, 16000)

    detector = KeywordDetector(model_path="D:\scam-call-detection\saved_model", scam_threshold=0.4)  # Lowered threshold to enhance sensitivity

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    st.write("**Speak a few words...**")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcription = preprocess_text(result.get("text", ""))
                if transcription.strip():
                    st.write(f"You said: {transcription}")
                    detection_result = detector.detect_keywords(transcription)
                    if detection_result["is_scam"]:
                        st.error(f"⚠️ Scam Alert: Confidence ({detection_result['confidence']:.2f})")
                    else:
                        st.success(f"✔️ Safe: Confidence ({detection_result['confidence']:.2f})")
                else:
                    logging.info("No valid speech detected.")
            else:
                partial_result = json.loads(recognizer.PartialResult())
                logging.debug("Partial: " + partial_result.get("partial", ""))

    except KeyboardInterrupt:
        logging.info("Stopped listening.")
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Real-Time Scam Call Detection System")
    start_listening_button = st.button("Start Listening")

    if start_listening_button:
        transcribe_audio()

if __name__ == "__main__":
    main()
