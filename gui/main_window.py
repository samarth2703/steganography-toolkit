from __future__ import annotations

from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from gui.compare_window import CompareTab
from gui.decode_tab import DecodeTab
from gui.encode_tab import EncodeTab
from gui.settings import APP_NAME, COLORS, FONT_BODY, FONT_TITLE


class SteganographyApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(980, 680)
        self.configure(fg_color=COLORS["background"])

        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        Path("input").mkdir(exist_ok=True)

        self._build_header()
        self.tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["panel"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["panel_alt"],
            text_color=COLORS["text"],
        )
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        encode_frame = self.tabs.add("Encode")
        decode_frame = self.tabs.add("Decode")
        compare_frame = self.tabs.add("Compare")
        settings_frame = self.tabs.add("Settings")

        self.encode_tab = EncodeTab(encode_frame, self)
        self.decode_tab = DecodeTab(decode_frame, self)
        self.compare_tab = CompareTab(compare_frame, self)
        self._build_settings(settings_frame)

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["background"])
        header.pack(fill="x", padx=18, pady=18)
        title = ctk.CTkLabel(header, text=APP_NAME.upper(), font=FONT_TITLE, text_color=COLORS["text"])
        title.pack(side="left")
        subtitle = ctk.CTkLabel(
            header,
            text="LSB image hiding, decoding, and bit-level learning",
            font=FONT_BODY,
            text_color=COLORS["muted"],
        )
        subtitle.pack(side="left", padx=18)

    def _build_settings(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        card = ctk.CTkFrame(parent, fg_color=COLORS["panel_alt"], corner_radius=8)
        card.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Export And Packaging", font=("Segoe UI", 19, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 6)
        )
        text = (
            "Saved encoded images go to the output folder by default.\n"
            "Decoded messages, binary previews, and logs can be exported from their tabs.\n\n"
            "To build a Windows app later:\n"
            "pip install pyinstaller\n"
            "pyinstaller --onefile --windowed app.py"
        )
        ctk.CTkLabel(card, text=text, justify="left", font=FONT_BODY, text_color=COLORS["muted"]).grid(
            row=1, column=0, sticky="w", padx=18, pady=8
        )

    def log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        self.encode_tab.append_log(line)
        self.decode_tab.append_log(line)
        self.compare_tab.append_log(line)

    def send_to_compare(self, original, encoded) -> None:
        self.compare_tab.set_images(original, encoded)
        self.tabs.set("Compare")
