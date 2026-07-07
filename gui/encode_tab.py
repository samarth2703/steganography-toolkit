from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from core.encoder import encode_image
from core.validator import capacity_bytes, human_size, validate_image_path
from core.visualizer import binary_message_preview, calculate_metrics, inspect_pixel, sample_bit_changes
from gui.settings import COLORS, FONT_BODY, FONT_HEADING, FONT_MONO


class EncodeTab(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color=COLORS["panel"])
        self.pack(fill="both", expand=True)
        self.app = app
        self.original_image: Image.Image | None = None
        self.encoded_image: Image.Image | None = None
        self.original_path: Path | None = None
        self.preview_ref = None
        self.encoded_preview_ref = None
        self.lsb_var = ctk.IntVar(value=1)
        self.password_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Load a PNG or BMP image to begin.")
        self.meta_var = ctk.StringVar(value="No image loaded")
        self.counter_var = ctk.StringVar(value="Characters: 0")
        self.metrics_var = ctk.StringVar(value="Quality metrics will appear after encoding.")
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1, uniform="cols")
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0)
        right = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(18, 9), pady=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(9, 18), pady=18)
        left.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._section_label(left, "Original Image", 0)
        self.preview = ctk.CTkLabel(left, text="No image selected", fg_color=COLORS["panel_alt"], corner_radius=8)
        self.preview.grid(row=1, column=0, sticky="nsew", pady=(8, 10))
        left.grid_rowconfigure(1, weight=1)
        ctk.CTkButton(left, text="Upload Image", command=self.load_image, fg_color=COLORS["accent"]).grid(
            row=2, column=0, sticky="ew", pady=4
        )
        ctk.CTkLabel(left, textvariable=self.meta_var, justify="left", text_color=COLORS["muted"]).grid(
            row=3, column=0, sticky="w", pady=8
        )

        self._section_label(right, "Secret Message", 0)
        self.message_box = ctk.CTkTextbox(right, height=150, font=FONT_BODY, fg_color=COLORS["panel_alt"])
        self.message_box.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        self.message_box.bind("<KeyRelease>", lambda _event: self.update_counter())
        ctk.CTkLabel(right, textvariable=self.counter_var, text_color=COLORS["muted"]).grid(row=2, column=0, sticky="w")

        controls = ctk.CTkFrame(right, fg_color="transparent")
        controls.grid(row=3, column=0, sticky="ew", pady=10)
        controls.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkEntry(controls, textvariable=self.password_var, placeholder_text="Password (optional)", show="*").grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ctk.CTkSegmentedButton(controls, values=["1 LSB", "2 LSB", "3 LSB"], command=self._set_lsb).grid(
            row=0, column=1, sticky="ew"
        )

        ctk.CTkButton(right, text="Encode Message", command=self.encode, fg_color=COLORS["accent"]).grid(
            row=4, column=0, sticky="ew", pady=4
        )
        action_row = ctk.CTkFrame(right, fg_color="transparent")
        action_row.grid(row=5, column=0, sticky="ew", pady=4)
        action_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(action_row, text="Save Image", command=self.save_image).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(action_row, text="Compare", command=self.compare).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.encoded_preview = ctk.CTkLabel(right, text="Encoded preview", fg_color=COLORS["panel_alt"], corner_radius=8)
        self.encoded_preview.grid(row=6, column=0, sticky="nsew", pady=10)
        right.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(right, textvariable=self.status_var, text_color=COLORS["success"], justify="left").grid(
            row=7, column=0, sticky="w", pady=(0, 4)
        )
        ctk.CTkLabel(right, textvariable=self.metrics_var, text_color=COLORS["muted"], justify="left").grid(
            row=8, column=0, sticky="w", pady=(0, 8)
        )

        lower = ctk.CTkFrame(self, fg_color=COLORS["panel_alt"], corner_radius=8)
        lower.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
        lower.grid_columnconfigure((0, 1, 2), weight=1)
        self.bits_text = self._mini_text(lower, "Binary Viewer", 0)
        self.change_text = self._mini_text(lower, "Bit Visualizer", 1)
        self.log_text = self._mini_text(lower, "Logs", 2)
        self.preview.bind("<Button-1>", self.inspect_pixel)

    def _section_label(self, parent, text: str, row: int) -> None:
        ctk.CTkLabel(parent, text=text, font=FONT_HEADING).grid(row=row, column=0, sticky="w")

    def _mini_text(self, parent, label: str, column: int):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=label, font=FONT_HEADING).grid(row=0, column=0, sticky="w")
        box = ctk.CTkTextbox(frame, height=120, font=FONT_MONO, fg_color=COLORS["panel"])
        box.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        return box

    def _set_lsb(self, value: str) -> None:
        self.lsb_var.set(int(value[0]))
        self.update_counter()

    def load_image(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp")])
        if not path:
            return
        try:
            image_path = validate_image_path(path)
            self.original_image = Image.open(image_path).convert("RGB")
            self.original_path = image_path
            self.encoded_image = None
            self._show_image(self.original_image, self.preview, "preview_ref")
            self.meta_var.set(self._metadata(image_path, self.original_image))
            self.status_var.set("Image loaded.")
            self.update_counter()
            self.app.log(f"Loaded image: {image_path.name}")
        except Exception as exc:
            messagebox.showerror("Could not load image", str(exc))

    def encode(self) -> None:
        if self.original_image is None:
            messagebox.showwarning("Image needed", "Load an image before encoding.")
            return
        message = self.message_box.get("1.0", "end-1c")
        try:
            result = encode_image(self.original_image, message, self.password_var.get(), self.lsb_var.get())
            self.encoded_image = result.image
            self._show_image(self.encoded_image, self.encoded_preview, "encoded_preview_ref")
            metrics = calculate_metrics(self.original_image, self.encoded_image)
            psnr = "infinite" if metrics.psnr == float("inf") else f"{metrics.psnr:.2f} dB"
            self.metrics_var.set(
                f"Payload: {human_size(result.payload_size)} | Changed channels: {result.changed_channels}\n"
                f"MSE: {metrics.mse:.6f} | PSNR: {psnr} | Quality: {metrics.quality_percent:.2f}%"
            )
            self.status_var.set("Message hidden successfully.")
            self._set_text(self.bits_text, binary_message_preview(message))
            self._set_text(self.change_text, sample_bit_changes(self.original_image, self.encoded_image))
            self.app.log("Hidden message successfully.")
        except Exception as exc:
            messagebox.showerror("Encoding failed", str(exc))

    def save_image(self) -> None:
        if self.encoded_image is None:
            messagebox.showwarning("Nothing to save", "Encode a message first.")
            return
        default = self.app.output_dir / "encoded_secret.png"
        path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=default.name, filetypes=[("PNG", "*.png")])
        if not path:
            return
        self.encoded_image.save(path)
        self.status_var.set(f"Saved encoded image: {Path(path).name}")
        self.app.log(f"Saved encoded image: {Path(path).name}")

    def compare(self) -> None:
        if self.original_image is None or self.encoded_image is None:
            messagebox.showwarning("Compare needs two images", "Encode an image first.")
            return
        self.app.send_to_compare(self.original_image, self.encoded_image)

    def update_counter(self) -> None:
        text = self.message_box.get("1.0", "end-1c")
        capacity = 0
        if self.original_image:
            capacity = capacity_bytes(self.original_image.width, self.original_image.height, 3, self.lsb_var.get())
        self.counter_var.set(f"Characters: {len(text)} | Capacity: {human_size(capacity)}")

    def inspect_pixel(self, event) -> None:
        if not self.original_image:
            return
        widget_width = max(self.preview.winfo_width(), 1)
        widget_height = max(self.preview.winfo_height(), 1)
        x = int(event.x / widget_width * self.original_image.width)
        y = int(event.y / widget_height * self.original_image.height)
        self._set_text(self.change_text, inspect_pixel(self.original_image, self.encoded_image, x, y))

    def _metadata(self, path: Path, image: Image.Image) -> str:
        capacity = capacity_bytes(image.width, image.height, 3, self.lsb_var.get())
        return (
            f"Filename: {path.name}\n"
            f"Resolution: {image.width} x {image.height}\n"
            f"Mode: RGB\n"
            f"Maximum capacity: {human_size(capacity)}"
        )

    def _show_image(self, image: Image.Image, label, attr: str) -> None:
        preview = image.copy()
        preview.thumbnail((500, 280))
        photo = ImageTk.PhotoImage(preview)
        setattr(self, attr, photo)
        label.configure(image=photo, text="")

    def _set_text(self, box, text: str) -> None:
        box.delete("1.0", "end")
        box.insert("1.0", text)

    def append_log(self, line: str) -> None:
        if hasattr(self, "log_text"):
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
