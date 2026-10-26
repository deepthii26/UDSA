"""Offline sentence-level emotion analysis for MoodSense.

VADER supplies sentiment-aware scoring (including negation and intensity),
while the small domain lexicon maps sentiment to the six emotions displayed by
the application. No model download or internet connection is required.
"""

import re
from collections import Counter
from typing import Dict, Tuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from emotion_data import EMOTIONS


_analyzer = SentimentIntensityAnalyzer()
_emotion_order = tuple(EMOTIONS)
_intensifiers = {"very", "really", "extremely", "so", "incredibly", "totally", "absolutely"}


def _word_matches(text: str, keyword: str) -> int:
    return len(re.findall(r"\b" + re.escape(keyword) + r"\b", text))


def analyze_emotion(text: str) -> Tuple[str, Dict[str, float]]:
    """Return ``(emotion_key, scores)`` using sentiment plus emotion cues."""
    if not isinstance(text, str) or not text.strip():
        return "neutral", {key: 0.0 for key in EMOTIONS}

    normalized = text.lower().replace('’', "'")
    text = text.replace('’', "'")
    sentiment = _analyzer.polarity_scores(text)
    compound = sentiment["compound"]
    scores = Counter({key: 0.0 for key in EMOTIONS})
    intensity = 1.0 + 0.15 * sum(word in normalized.split() for word in _intensifiers)

    cue_counts = {}
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|[.!?,;]", normalized)
    negators = {'not', 'no', 'never', 'neither', 'hardly', 'without'}
    for key, emotion in EMOTIONS.items():
        matches = 0
        for index, word in enumerate(tokens):
            if word not in emotion.keywords:
                continue
            preceding = tokens[max(0, index - 3):index]
            # Limit negation to the nearby clause, rather than counting
            # "not angry" as an explicit anger cue.
            for boundary in ('.', '!', '?', ',', ';', 'but'):
                if boundary in preceding:
                    preceding = preceding[len(preceding) - preceding[::-1].index(boundary):]
            if any(item in negators or item.endswith("n't") for item in preceding):
                continue
            matches += 1
        # Also support emoji typed directly inside a sentence, e.g. "I feel great 😊".
        matches += text.replace('\ufe0f', '').count(emotion.emoji.replace('\ufe0f', '')) * 3
        cue_counts[key] = matches
        scores[key] += matches * intensity

    # VADER's phrase-level result provides the general emotional direction.
    scores["happy"] += max(compound, 0.0) * 2.0
    scores["sad"] += max(-compound, 0.0) * 1.45
    if sentiment["neg"] > 0.35 and cue_counts["angry"] == 0:
        scores["sad"] += sentiment["neg"]
    if sentiment["pos"] > 0.35:
        scores["happy"] += sentiment["pos"]

    # Explicit anger is more informative than the generic negative VADER
    # score, so preserve it for phrases such as "extremely angry".
    if cue_counts["angry"]:
        scores["angry"] += 1.5 * cue_counts["angry"]
    if cue_counts["love"]:
        scores["love"] += 1.8 * cue_counts["love"]
    if cue_counts["surprised"]:
        scores["surprised"] += 1.8 * cue_counts["surprised"]

    if max(scores.values()) == 0:
        return "neutral", dict(scores)
    winner = max(scores, key=lambda key: (scores[key], -_emotion_order.index(key)))
    return winner, dict(scores)


def detect_emotion(text: str) -> str:
    """Backward-compatible convenience function returning only the key."""
    return analyze_emotion(text)[0]


def emotion_label(key: str) -> str:
    return EMOTIONS.get(key, EMOTIONS["neutral"]).label
