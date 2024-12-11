import unittest
from src.audio_transcription import transcribe_audio
from src.keyword_detection import KeywordDetector
from unittest.mock import patch, MagicMock

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.detector = KeywordDetector(model_path="models/distilbert_model")

    @patch('src.audio_transcription.stream.read')
    def test_transcribe_audio_integration(self, mock_read):
        mock_read.side_effect = [b"audio snippet", b"audio snippet"]
        with patch('src.audio_transcription.KaldiRecognizer') as MockRecognizer:
            mock_recognizer = MockRecognizer.return_value
            mock_recognizer.AcceptWaveform.return_value = True
            mock_recognizer.Result.return_value = '{"text": "example scam message"}'

            # Run the transcribe_audio function
            with patch.object(self.detector, 'detect_keywords') as mock_detect:
                mock_detect.return_value = {"is_scam": True, "confidence": 0.9}

                transcribe_audio()

                # Test if the detector detected a scam
                mock_detect.assert_called_with("example scam message")
                print("Integration test passed.")

    @patch('src.audio_transcription.stream.read')
    def test_transcribe_audio_integration_safe(self, mock_read):
        mock_read.side_effect = [b"audio snippet", b"audio snippet"]
        with patch('src.audio_transcription.KaldiRecognizer') as MockRecognizer:
            mock_recognizer = MockRecognizer.return_value
            mock_recognizer.AcceptWaveform.return_value = True
            mock_recognizer.Result.return_value = '{"text": "example safe message"}'

            # Run the transcribe_audio function
            with patch.object(self.detector, 'detect_keywords') as mock_detect:
                mock_detect.return_value = {"is_scam": False, "confidence": 0.7}

                transcribe_audio()

                # Test if the detector did not classify as scam
                mock_detect.assert_called_with("example safe message")
                print("Integration test (safe case) passed.")

if __name__ == "__main__":
    unittest.main()
