# MoodSense

MoodSense is an offline Python application that detects a user's emotion from typed text or an emoji selection and adapts a polished Three.js interface accordingly.

## Problem statement

Traditional interfaces look the same regardless of how a user feels. MoodSense demonstrates an emotion-adaptive user interface: the detected emotion changes the application's colors, selected emoji, status, and supportive message.

## Objective

Build a polished, easy-to-explain GUI that demonstrates rule-based emotion detection without an internet connection, API keys, or machine-learning services.

## Features

- Analyzes typed sentences with the offline VADER sentiment analyzer, including negation, punctuation, capitalization, and intensity.
- Starts with a genuinely empty text area so the user controls the input.
- Detects emojis typed inside sentences, such as `I feel great 😊`.
- Six large emoji buttons for instant selection.
- Adaptive background, accent colors, result card, emoji, and message.
- Empty-input validation and safe fallback to Neutral.
- Reset control and responsive card-based layout.
- Fully offline after installing Python dependencies; Three.js is bundled locally in `web/vendor`.

## Three.js experience

The result card is rendered as a local Three.js scene rather than a static Tkinter drawing. It includes a softly animated 3D mood orb, expressive eyes, brows, mouth scaling, emotion-specific lighting, floating particles, and subtle idle motion. The Python detector remains the source of truth: the browser sends text to the local Python endpoint and receives the detected emotion.

## Technologies

- Python 3
- CustomTkinter
- Standard library modules: `dataclasses`, `re`, and `collections`
- VADER Sentiment (`vaderSentiment`), bundled with its lexicon and usable offline

## How detection works

The detector uses VADER to analyze the complete sentence, including context such as negation (`not happy`) and intensity (`VERY happy`). Distinctive emotion cues are then mapped to the six supported UI categories, with VADER's positive/negative score used as a general sentiment signal. If there is no meaningful signal, the application returns Neutral. This is more natural than checking only one exact keyword while remaining deterministic and easy to explain in a viva.

## Supported emotions

| Emotion | Example keywords |
| --- | --- |
| 😊 Happy | happy, joyful, great, awesome, smile |
| 😢 Sad | sad, lonely, upset, hurt, disappointed |
| 😡 Angry | angry, mad, furious, annoyed, frustrated |
| ❤️ Love | love, lovely, caring, adore, heart |
| 😲 Surprised | surprised, shocked, wow, unexpected, amazed |
| 😐 Neutral | okay, fine, normal, alright, nothing |

## Project structure

```text
MoodSense/
├── main.py              # Application entry point
├── web_app.py           # Local HTTP server and Python/JS bridge
├── emotion_data.py      # Emotion metadata, themes, and messages
├── emotion_detector.py  # VADER + emotion-category analysis
├── ui.py                # Legacy CustomTkinter interface
├── web/                 # Three.js frontend and local vendor bundle
├── requirements.txt     # Runtime dependency
└── README.md
```

## Installation and running

1. Install Python 3.10 or newer.
2. Open a terminal in this project directory.
3. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the dependency:

   ```powershell
   pip install -r requirements.txt
   ```

5. Start MoodSense. This opens the new Three.js interface in your browser:

   ```powershell
   python main.py
   ```

The current interface is browser-based because Three.js is a WebGL library. The Python server is local-only (`127.0.0.1`) and does not call any external API.

### Running from VS Code

Open this project folder, then run `python main.py` in the integrated terminal
or use the **Run MoodSense** F5 configuration. Keep that terminal running.
Use the browser URL printed by Python. Opening `index.html` directly or using
VS Code Live Server does not start the Python analysis endpoint.
After updating the project, stop the old server with Ctrl+C, run it again,
and use the newly opened browser tab.

Both `web/vendor/three.module.js` and `web/vendor/three.core.js` are required.
The interface keeps analysis and emoji selection available even when WebGL
cannot initialize, displaying a regular emoji instead.

### Browser regression checks

Optional development check (Microsoft Edge must be installed):

```powershell
python -m pip install playwright
python test_browser.py
```

This exercises actual browser clicks, Python analysis, the 3D canvas, all six
emoji selections, empty input, reset, graphics failure, and network errors.
VADER is still a heuristic English sentiment analyzer: sarcasm, long mixed
statements, and unsupported languages are not reliably understood. The scores
are heuristic weights, not confidence probabilities.

## Edge cases handled

- Empty or whitespace-only input: shows a validation message without crashing.
- Unknown text with no meaningful signal: returns Neutral with a reassuring message.
- Typed emoji input: recognizes all six supported emojis inside a sentence.
- Mixed signals: distinctive cues such as `furious` or `love` take priority over broad sentiment.
- Repeated detections and emoji clicks: update existing widgets without duplication.
- Invalid detector input such as `None`: safely falls back to Neutral.
- Reset: clears the text area and restores the Neutral state.

## Example inputs and outputs

- `I am very happy today` → 😊 Happy
- `I feel lonely and sad` → 😢 Sad
- `I am extremely angry` → 😡 Angry
- `I love this so much` → ❤️ Love
- `Wow, I didn't expect this!` → 😲 Surprised
- `I am okay` → 😐 Neutral
- `The clouds are above the building` → 😐 Neutral

Clicking Detect Emotion with an empty box shows a validation message instead of crashing. The Reset button restores the welcome text and Neutral result state.

## Future enhancements

- Add a user-editable keyword dictionary.
- Add a history panel with timestamped detections.
- Add optional sentiment intensity scoring.
- Add localization for multiple languages.
