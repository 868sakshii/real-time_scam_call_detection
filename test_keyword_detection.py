import unittest
from src.keyword_detection import KeywordDetector

class TestKeywordDetector(unittest.TestCase):

    def setUp(self):
        self.detector = KeywordDetector(model_path="")

    def test_detect_keywords(self):
        # Test with scam text
        result = self.detector.detect_keywords("Claim your free gift card now by clicking this link")
        self.assertTrue(result["is_scam"], "Should identify scam message")
        self.assertGreater(result["confidence"], 0.8, "Confidence should be high")

        # Test with safe text
        result = self.detector.detect_keywords("Hello, how are you today?")
        self.assertFalse(result["is_scam"], "Should not identify as scam")
        self.assertGreater(result["confidence"], 0.5, "Confidence should be moderate")

if __name__ == "__main__":
    unittest.main()
