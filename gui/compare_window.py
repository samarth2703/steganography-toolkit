from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from core.visualizer import bit_plane_image, calculate_metrics, create_difference_image
from gui.settings import COLORS, FONT_HEADING, FONT_MONO


class CompareTab(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color=COLORS["panel"])
        self.pack(fill="both", expand=True)
        self.app = app
        self.original: Image.Image | None = None
        self.encoded: Image.Image | None = None
        self.diff: Image.Image | None = None
        self.refs = {}
        self.metrics_var = ctk.StringVar(value="Send an encoded image here from the Encode tab.")
        self.bit_var = ctk.IntVar(value=0)
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="cols")
        self.grid_rowconfigure(1, weight=1)

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=0, column=0, columnspan=3, sticky="ew", padx=18, pady=(18, 8))
        controls.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(controls, text="Load Original", command=self.load_original).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(controls, text="Load Encoded", command=self.load_encoded).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(controls, textvariable=self.metrics_var, text_color=COLORS["muted"]).grid(row=0, column=2, sticky="e")

        self.original_label = self._image_panel("Original", 0)
        self.encoded_label = self._image_panel("Encoded", 1)
        self.diff_label = self._image_panel("Difference x80", 2)

        bottom = ctk.CTkFrame(self, fg_color=COLORS["panel_alt"], corner_radius=8)
        bottom.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(8, 18))
        bottom.grid_columnconfigure((0, 1), weight=1)

        plane_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        plane_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        plane_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(plane_frame, text="Bit Plane Viewer", font=FONT_HEADING).grid(row=0, column=0, sticky="w")
        self.plane_label = ctk.CTkLabel(plane_frame, text="Bit plane preview", fg_color=COLORS["panel"], corner_radius=8)
        self.plane_label.grid(row=1, column=0, sticky="nsew", pady=8)
        ctk.CTkSlider(plane_frame, from_=0, to=7, number_of_steps=7, command=self._set_bit).grid(
            row=2, column=0, sticky="ew"
        )

        log_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        log_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_frame, text="Logs", font=FONT_HEADING).grid(row=0, column=0, sticky="w")
        self.log_text = ctk.CTkTextbox(log_frame, height=150, font=FONT_MONO, fg_color=COLORS["panel"])
        self.log_text.grid(row=1, column=0, sticky="nsew", pady=8)

    def _image_panel(self, title: str, column: int):
        frame = ctk.CTkFrame(self, fg_color=COLORS["panel_alt"], corner_radius=8)
        frame.grid(row=1, column=column, sticky="nsew", padx=9, pady=8)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=title, font=FONT_HEADING).grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))
        label = ctk.CTkLabel(frame, text="No image", fg_color=COLORS["panel"], corner_radius=8)
        label.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        return label

    def load_original(self) -> None:
        image = self._load_image()
        if image:
            self.original = image
            self._refresh()

    def load_encoded(self) -> None:
        image = self._load_image()
        if image:
            self.encoded = image
            self._refresh()

    def _load_image(self) -> Image.Image | None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp")])
        if not path:
            return None
        try:
            return Image.open(path).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Could not load image", str(exc))
            return None

    def set_images(self, original: Image.Image, encoded: Image.Image) -> None:
        self.original = original
        self.encoded = encoded
        self._refresh()
        self.app.log("Opened image comparison.")

    def _refresh(self) -> None:
        if self.original:
            self._show(self.original, self.original_label, "original")
        if self.encoded:
            self._show(self.encoded, self.encoded_label, "encoded")
            self._show(bit_plane_image(self.encoded, self.bit_var.get()), self.plane_label, "plane")
        if self.original and self.encoded:
            if self.original.size != self.encoded.size:
                self.metrics_var.set("Images must be the same size for comparison.")
                return
            self.diff = create_difference_image(self.original, self.encoded)
            self._show(self.diff, self.diff_label, "diff")
            metrics = calculate_metrics(self.original, self.encoded)
            psnr = "infinite" if metrics.psnr == float("inf") else f"{metrics.psnr:.2f} dB"
            self.metrics_var.set(f"MSE: {metrics.mse:.6f} | PSNR: {psnr} | Quality: {metrics.quality_percent:.2f}%")

    def _set_bit(self, value) -> None:
        self.bit_var.set(int(float(value)))
        if self.encoded:
            self._show(bit_plane_image(self.encoded, self.bit_var.get()), self.plane_label, "plane")

    def _show(self, image: Image.Image, label, key: str) -> None:
        preview = image.copy()
        preview.thumbnail((360, 330))
        photo = ImageTk.PhotoImage(preview)
        self.refs[key] = photo
        label.configure(image=photo, text="")

    def append_log(self, line: str) -> None:
        if hasattr(self, "log_text"):
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
