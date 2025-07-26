import unittest
from src.utils import classify_action, parse_sentiment_line

class TestSignalLogic(unittest.TestCase):

    def test_classify_action_short(self):
        sentiment = "NEGATIVE (0.95)"
        action = classify_action(sentiment)
        self.assertEqual(action, "SHORT")

    def test_classify_action_neutral(self):
        sentiment = "NEUTRAL (0.70)"
        action = classify_action(sentiment)
        self.assertEqual(action, "NEUTRAL")

    def test_parse_sentiment_line(self):
        line = "NEGATIVE (0.95): inflation concerns remain high despite fed actions"
        sentiment, headline = parse_sentiment_line(line)
        self.assertEqual(sentiment, "NEGATIVE (0.95)")
        self.assertEqual(headline, "inflation concerns remain high despite fed actions")

if __name__ == '__main__':
    unittest.main()