"""CustomTkinter user interface for MoodSense."""

import math
import tkinter as tk

import customtkinter as ctk

from emotion_data import EMOTIONS, EMOTION_ORDER
from emotion_detector import analyze_emotion


class AnimatedMoodFace(tk.Canvas):
    """Lightweight vector face that blinks and animates its expression."""

    def __init__(self, master, **kwargs):
        super().__init__(master, width=190, height=170, highlightthickness=0, **kwargs)
        self.key = "neutral"
        self.accent = "#64748B"
        self.face_fill = "#FFFDF8"
        self.phase = 0.0
        self.blinking = False
        self._animation_id = None
        self._blink_id = None
        self._blink_finish_id = None
        self._draw()
        self._animation_id = self.after(70, self._animate)
        self._blink_id = self.after(3200, self._blink)

    def set_emotion(self, key: str, accent: str, background: str) -> None:
        self.key, self.accent = key, accent
        self.face_fill = "#FFFDF8" if key not in {"sad", "neutral"} else "#F8FBFF"
        self.configure(bg=background)
        self._draw()

    def _blink(self) -> None:
        self.blinking = True
        self._draw()
        self._blink_finish_id = self.after(150, self._finish_blink)
        self._blink_id = self.after(3000, self._blink)

    def _finish_blink(self) -> None:
        self.blinking = False
        self._draw()

    def _animate(self) -> None:
        self.phase += 0.12
        self._draw()
        self._animation_id = self.after(70, self._animate)

    def stop(self) -> None:
        """Cancel animation callbacks before the Tk window is destroyed."""
        for callback_id in (self._animation_id, self._blink_id, self._blink_finish_id):
            if callback_id:
                try:
                    self.after_cancel(callback_id)
                except tk.TclError:
                    pass
        self._animation_id = self._blink_id = self._blink_finish_id = None

    def _draw(self) -> None:
        self.delete("all")
        pulse = 1.0 + (0.035 * math.sin(self.phase)) if self.key in {"happy", "love", "surprised"} else 1.0
        cx, cy, radius = 95, 82, 59 * pulse
        self.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=self.face_fill, outline=self.accent, width=5)

        if self.key == "angry":
            self.create_line(62, 58, 80, 65, fill="#381712", width=5, capstyle="round")
            self.create_line(110, 65, 128, 58, fill="#381712", width=5, capstyle="round")
        elif self.key == "sad":
            self.create_arc(60, 55, 83, 76, start=200, extent=140, style="arc", outline="#23405F", width=4)
            self.create_arc(107, 55, 130, 76, start=200, extent=140, style="arc", outline="#23405F", width=4)
        elif self.key == "surprised":
            self.create_arc(59, 51, 83, 70, start=20, extent=140, style="arc", outline="#33256D", width=4)
            self.create_arc(107, 51, 131, 70, start=20, extent=140, style="arc", outline="#33256D", width=4)

        if self.blinking:
            self.create_line(62, 78, 79, 78, fill="#17202A", width=4, capstyle="round")
            self.create_line(111, 78, 128, 78, fill="#17202A", width=4, capstyle="round")
        elif self.key == "surprised":
            self.create_oval(63, 69, 79, 88, fill="#17202A", outline="")
            self.create_oval(111, 69, 127, 88, fill="#17202A", outline="")
        else:
            self.create_oval(63, 72, 79, 84, fill="#17202A", outline="")
            self.create_oval(111, 72, 127, 84, fill="#17202A", outline="")

        if self.key == "love":
            self.create_text(71, 78, text="♥", fill="#D84A75", font=("Segoe UI", 18, "bold"))
            self.create_text(119, 78, text="♥", fill="#D84A75", font=("Segoe UI", 18, "bold"))
        elif self.key == "happy":
            self.create_arc(60, 76, 130, 125, start=200, extent=140, style="arc", outline="#17202A", width=5)
            self.create_oval(83, 105, 107, 115, fill="#FF9A9A", outline="")
        elif self.key == "sad":
            self.create_arc(67, 99, 123, 133, start=20, extent=140, style="arc", outline="#17202A", width=5)
            self.create_oval(129, 87, 135, 98, fill="#62A6E8", outline="")
        elif self.key == "angry":
            self.create_arc(72, 99, 118, 124, start=20, extent=140, style="arc", outline="#17202A", width=5)
        elif self.key == "surprised":
            mouth = 12 + int(3 * math.sin(self.phase))
            self.create_oval(95 - mouth, 102 - mouth, 95 + mouth, 102 + mouth + 8, fill="#38202A", outline="")
        elif self.key == "love":
            self.create_text(95, 108, text="♥", fill="#D84A75", font=("Segoe UI", 25, "bold"))
        else:
            self.create_line(75, 106, 115, 106, fill="#17202A", width=4, capstyle="round")


class MoodSenseApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.current_key = "neutral"
        self._buttons = {}
        self._setup_window()
        self._build_ui()
        self._apply_emotion("neutral")

    def destroy(self) -> None:
        if hasattr(self, "face"):
            self.face.stop()
        super().destroy()

    def _setup_window(self) -> None:
        self.title("MoodSense — Emotion-Adaptive UI")
        self.geometry("1080x760")
        self.minsize(820, 650)
        self.configure(fg_color="#F4F6F8")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=48, pady=(30, 12))
        self.header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.header, text="MoodSense", font=ctk.CTkFont(size=32, weight="bold"), text_color="#17202A").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.header, text="An Emotion-Adaptive User Interface", font=ctk.CTkFont(size=15), text_color="#64748B").grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.status_label = ctk.CTkLabel(self.header, text="●  Ready to listen", font=ctk.CTkFont(size=13, weight="bold"), text_color="#64748B")
        self.status_label.grid(row=0, column=1, rowspan=2, sticky="e")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=48, pady=(8, 34))
        self.content.grid_columnconfigure(0, weight=3)
        self.content.grid_columnconfigure(1, weight=2)
        self.content.grid_rowconfigure(0, weight=1)
        self.input_card = ctk.CTkFrame(self.content, corner_radius=22, fg_color="#FFFFFF")
        self.input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.input_card.grid_columnconfigure(0, weight=1)
        self.input_card.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self.input_card, text="How are you feeling?", font=ctk.CTkFont(size=22, weight="bold"), text_color="#17202A").grid(row=0, column=0, sticky="w", padx=28, pady=(28, 4))
        ctk.CTkLabel(self.input_card, text="Write a sentence, include an emoji, or use the buttons below.", font=ctk.CTkFont(size=13), text_color="#64748B").grid(row=1, column=0, sticky="w", padx=28, pady=(0, 6))
        ctk.CTkLabel(self.input_card, text="Example: I completed my project and feel amazing 😊", font=ctk.CTkFont(size=12, slant="italic"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=28, pady=(0, 12))
        self.text_box = ctk.CTkTextbox(self.input_card, height=155, corner_radius=14, border_width=1, border_color="#E2E8F0", fg_color="#F8FAFC", text_color="#1E293B", font=ctk.CTkFont(size=14), wrap="word")
        self.text_box.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 15))
        self.detect_button = ctk.CTkButton(self.input_card, text="Analyze My Mood  →", height=46, corner_radius=12, font=ctk.CTkFont(size=14, weight="bold"), command=self._detect_from_text)
        self.detect_button.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 28))

        self.result_card = ctk.CTkFrame(self.content, corner_radius=22, fg_color="#FFFFFF")
        self.result_card.grid(row=0, column=1, sticky="nsew")
        self.result_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.result_card, text="YOUR MOOD", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, pady=(28, 2))
        self.face = AnimatedMoodFace(self.result_card, bg="#FFFFFF")
        self.face.grid(row=1, column=0, pady=(0, 3))
        ctk.CTkLabel(self.result_card, text="Detected Emotion", font=ctk.CTkFont(size=13), text_color="#64748B").grid(row=2, column=0)
        self.result_label = ctk.CTkLabel(self.result_card, text="NEUTRAL", font=ctk.CTkFont(size=25, weight="bold"), text_color="#1E293B")
        self.result_label.grid(row=3, column=0, pady=(3, 16))
        self.message_label = ctk.CTkLabel(self.result_card, text="", wraplength=260, justify="center", font=ctk.CTkFont(size=14), text_color="#334155")
        self.message_label.grid(row=4, column=0, padx=28, pady=(0, 30))

        ctk.CTkLabel(self, text="CHOOSE AN EMOJI", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").grid(row=2, column=0, sticky="w", padx=48, pady=(0, 10))
        self.emoji_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.emoji_bar.grid(row=3, column=0, sticky="ew", padx=48, pady=(0, 28))
        for index, key in enumerate(EMOTION_ORDER):
            self.emoji_bar.grid_columnconfigure(index, weight=1)
            emotion = EMOTIONS[key]
            button = ctk.CTkButton(self.emoji_bar, text=f"{emotion.emoji}  {emotion.label}", height=44, corner_radius=12, fg_color="#FFFFFF", hover_color="#E2E8F0", text_color="#334155", border_width=1, border_color="#E2E8F0", font=ctk.CTkFont(size=13, weight="bold"), command=lambda selected=key: self._apply_emotion(selected))
            button.grid(row=0, column=index, sticky="ew", padx=4)
            self._buttons[key] = button
        ctk.CTkButton(self, text="↺  Reset", width=110, height=34, corner_radius=10, fg_color="transparent", hover_color="#E2E8F0", text_color="#64748B", command=self._reset).grid(row=4, column=0, pady=(0, 22))

    def _detect_from_text(self) -> None:
        text = self.text_box.get("1.0", "end").strip()
        if not text:
            self.status_label.configure(text="●  Please enter some text", text_color="#C9553B")
            self.message_label.configure(text="Please enter how you're feeling first.")
            return
        self._apply_emotion(analyze_emotion(text)[0])

    def _apply_emotion(self, key: str) -> None:
        emotion = EMOTIONS.get(key, EMOTIONS["neutral"])
        self.current_key = emotion.key
        self.configure(fg_color=emotion.background)
        self.result_card.configure(fg_color=emotion.surface)
        self.input_card.configure(fg_color=emotion.surface)
        self.face.set_emotion(emotion.key, emotion.accent, emotion.surface)
        self.result_label.configure(text=emotion.label.upper(), text_color=emotion.text)
        self.message_label.configure(text=emotion.message)
        self.detect_button.configure(fg_color=emotion.accent, hover_color=emotion.accent_hover)
        self.status_label.configure(text=f"●  Mood detected: {emotion.label}", text_color=emotion.accent)
        for button_key, button in self._buttons.items():
            selected = button_key == emotion.key
            button.configure(fg_color=emotion.accent if selected else "#FFFFFF", hover_color=emotion.accent_hover if selected else "#E2E8F0", text_color="#FFFFFF" if selected else "#334155", border_color=emotion.accent if selected else "#E2E8F0")

    def _reset(self) -> None:
        self.text_box.delete("1.0", "end")
        self._apply_emotion("neutral")
        self.status_label.configure(text="●  Ready to listen", text_color="#64748B")


def run() -> None:
    app = MoodSenseApp()
    app.mainloop()
