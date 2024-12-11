import streamlit as st
import pyaudio
from vosk import Model, KaldiRecognizer
import json
import re
import os
from src.keyword_detection import KeywordDetector

# Path to the English Vosk model
MODEL_PATH = r"D:\scam-call-detection\models\vosk_model\vosk-model-small-en-in-0.4"

def load_model():
    """
    Load the Vosk model for English.
    """
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model path is invalid: {MODEL_PATH}")
        st.stop()
    return Model(MODEL_PATH)

def preprocess_text(text):
    """
    Preprocess the input text to clean unnecessary characters and normalize it.
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)  # Remove URLs
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    return text

def transcribe_audio():
    """
    Transcribe audio from the microphone and display results on Streamlit.
    """
    # Load the model
    model = load_model()
    recognizer = KaldiRecognizer(model, 16000)
    detector = KeywordDetector(model_path="D:\scam-call-detection\saved_model", scam_threshold=0.4)

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    st.write("**Listening... Speak into the microphone!**")

    try:
        while True:
            # Read audio data
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                # Parse the recognized text
                result = json.loads(recognizer.Result())
                transcription = preprocess_text(result.get("text", ""))
                if transcription.strip():
                    # Display transcription
                    st.write(f"**You said:** {transcription}")
                    
                    # Keyword detection
                    detection_result = detector.detect_keywords(transcription)
                    if detection_result["is_scam"]:
                        # Update session state
                        st.session_state["popup"] = True
                        st.session_state["transcription"] = transcription
                        st.session_state["confidence"] = detection_result["confidence"]
                        return  # Exit loop when scam is detected
                    else:
                        st.success(f"✔️ Safe: Confidence ({detection_result['confidence']:.2f})")
                else:
                    st.info("No valid speech detected. Please try again.")
    except KeyboardInterrupt:
        st.warning("Stopped listening.")
    except Exception as e:
        st.error(f"Error during transcription: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def main():
    """
    Main Streamlit app.
    """
    # Initialize session state variables
    if "popup" not in st.session_state:
        st.session_state["popup"] = False
        st.session_state["transcription"] = ""
        st.session_state["confidence"] = 0.0

    st.title("Real-Time Scam Call Detection System")
    st.write("Click the button below to start listening and detecting potential scam calls.")

    # Check if the scam detection popup should be displayed
    if st.session_state["popup"]:
        # Display popup-like UI
        st.error("⚠️ Scam Detected!")
        st.write(f"**Transcription:** {st.session_state['transcription']}")
        st.write(f"**Confidence:** {st.session_state['confidence']:.2f}")
        
        # Display buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Stop", key="stop"):
                st.session_state["popup"] = False
                st.warning("Stopped the Call.")
        with col2:
            if st.button("Proceed", key="proceed"):
                st.session_state["popup"] = False
                st.info("Proceeding despite scam detection. Be cautious!")
    else:
        if st.button("Start Listening"):
            transcribe_audio()

if __name__ == "__main__":
    main()
