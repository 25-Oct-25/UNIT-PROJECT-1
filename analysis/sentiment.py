"""
Contains natural language analysis tools for comment sentiment
and keyword extraction.
Uses VADER sentiment analysis from NLTK.
"""
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

def analyze_sentiment(comments):
    '''Analyze the sentiment of a list of comments using VADER'''
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(c) for c in comments]

    labels = []
    for s in sentiments:
        if s["compound"] >= 0.35:
            labels.append("positive")
        elif s["compound"] <= -0.35:
            labels.append("negative")
        else:
            labels.append("neutral")

    summary = Counter(labels)
    total = len(labels)
    distribution = {k: round(v / total * 100, 2) for k, v in summary.items()}
    return labels, distribution


def top_words(comments, n=20):
    '''Identify the most frequently used words in the comments'''
    text = " ".join(comments).lower()
    words = re.findall(r'\b[a-z]+\b', text)
    stopwords = set("the and to a of in it for is on this that you your are is".split())
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    return Counter(filtered).most_common(n)
