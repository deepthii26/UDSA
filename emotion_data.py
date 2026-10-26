"""Static emotion metadata used by the MoodSense application."""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Emotion:
    key: str
    label: str
    emoji: str
    keywords: Tuple[str, ...]
    background: str
    surface: str
    accent: str
    accent_hover: str
    text: str
    message: str


EMOTIONS: Dict[str, Emotion] = {
    "happy": Emotion(
        "happy", "Happy", "😊",
        ("happy", "joyful", "excited", "great", "amazing", "wonderful", "good", "awesome", "fun", "smile"),
        "#FFF7E6", "#FFFFFF", "#F59E0B", "#D97706", "#3D2A10",
        "That's wonderful! Keep enjoying the moment! 🌟",
    ),
    "sad": Emotion(
        "sad", "Sad", "😢",
        ("sad", "unhappy", "lonely", "depressed", "upset", "crying", "hurt", "bad", "disappointed"),
        "#EEF4FB", "#FFFFFF", "#4F86C6", "#3B6FA8", "#172A42",
        "It's okay to have difficult moments. Be gentle with yourself today. 💙",
    ),
    "angry": Emotion(
        "angry", "Angry", "😡",
        ("angry", "mad", "furious", "annoyed", "irritated", "hate", "frustrated", "rage"),
        "#FFF0ED", "#FFFFFF", "#E76F51", "#C9553B", "#421812",
        "Take a slow breath. A little space can help things feel manageable. 🌿",
    ),
    "love": Emotion(
        "love", "Love", "❤️",
        ("love", "lovely", "caring", "affection", "adore", "romantic", "heart"),
        "#FFF0F5", "#FFFFFF", "#D84A75", "#B9345B", "#451526",
        "What a beautiful feeling! Let that warmth brighten your day. 💗",
    ),
    "surprised": Emotion(
        "surprised", "Surprised", "😲",
        ("surprised", "shocked", "unexpected", "wow", "unbelievable", "amazed"),
        "#F2EEFF", "#FFFFFF", "#7C5CFC", "#6042DB", "#261A5C",
        "What an unexpected moment! Stay curious and enjoy the discovery. ✨",
    ),
    "neutral": Emotion(
        "neutral", "Neutral", "😐",
        ("normal", "okay", "fine", "alright", "nothing", "neutral"),
        "#F4F6F8", "#FFFFFF", "#64748B", "#475569", "#1E293B",
        "I'm not sure how you're feeling, but that's completely okay.",
    ),
}

EMOTION_ORDER = ("happy", "sad", "angry", "love", "surprised", "neutral")
