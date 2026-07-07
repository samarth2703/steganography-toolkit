from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from core.decoder import decode_image
from core.validator import capacity_bytes, human_size, validate_image_path
from core.visualizer import binary_message_preview
from gui.settings import COLORS, FONT_BODY, FONT_HEADING, FONT_MONO


class DecodeTab(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color=COLORS["panel"])
        self.pack(fill="both", expand=True)
        self.app = app
        self.image: Image.Image | None = None
        self.image_path: Path | None = None
        self.preview_ref = None
        self.lsb_var = ctk.IntVar(value=1)
        self.password_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Load an encoded image to reveal a message.")
        self.meta_var = ctk.StringVar(value="No image loaded")
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
        left.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="Encoded Image", font=FONT_HEADING).grid(row=0, column=0, sticky="w")
        self.preview = ctk.CTkLabel(left, text="No image selected", fg_color=COLORS["panel_alt"], corner_radius=8)
        self.preview.grid(row=1, column=0, sticky="nsew", pady=(8, 10))
        ctk.CTkButton(left, text="Load Encoded Image", command=self.load_image, fg_color=COLORS["accent"]).grid(
            row=2, column=0, sticky="ew", pady=4
        )
        ctk.CTkLabel(left, textvariable=self.meta_var, justify="left", text_color=COLORS["muted"]).grid(
            row=3, column=0, sticky="w", pady=8
        )

        ctk.CTkLabel(right, text="Hidden Message", font=FONT_HEADING).grid(row=0, column=0, sticky="w")
        controls = ctk.CTkFrame(right, fg_color="transparent")
        controls.grid(row=1, column=0, sticky="ew", pady=(8, 10))
        controls.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkEntry(controls, textvariable=self.password_var, placeholder_text="Password if needed", show="*").grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        ctk.CTkSegmentedButton(controls, values=["1 LSB", "2 LSB", "3 LSB"], command=self._set_lsb).grid(
            row=0, column=1, sticky="ew"
        )

        self.message_box = ctk.CTkTextbox(right, font=FONT_BODY, fg_color=COLORS["panel_alt"])
        self.message_box.grid(row=2, column=0, sticky="nsew")
        ctk.CTkButton(right, text="Decode Message", command=self.decode, fg_color=COLORS["accent"]).grid(
            row=3, column=0, sticky="ew", pady=(10, 4)
        )
        action_row = ctk.CTkFrame(right, fg_color="transparent")
        action_row.grid(row=4, column=0, sticky="ew", pady=4)
        action_row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(action_row, text="Copy", command=self.copy_message).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(action_row, text="Export TXT", command=self.export_message).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ctk.CTkButton(action_row, text="Export Binary", command=self.export_binary).grid(
            row=0, column=2, sticky="ew", padx=(6, 0)
        )
        ctk.CTkLabel(right, textvariable=self.status_var, text_color=COLORS["success"]).grid(
            row=5, column=0, sticky="w", pady=(8, 0)
        )

        lower = ctk.CTkFrame(self, fg_color=COLORS["panel_alt"], corner_radius=8)
        lower.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
        lower.grid_columnconfigure((0, 1), weight=1)
        self.binary_text = self._mini_text(lower, "Binary Viewer", 0)
        self.log_text = self._mini_text(lower, "Logs", 1)

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

    def load_image(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp")])
        if not path:
            return
        try:
            image_path = validate_image_path(path)
            self.image = Image.open(image_path).convert("RGB")
            self.image_path = image_path
            self._show_image(self.image)
            capacity = capacity_bytes(self.image.width, self.image.height, 3, self.lsb_var.get())
            self.meta_var.set(
                f"Filename: {image_path.name}\n"
                f"Resolution: {self.image.width} x {self.image.height}\n"
                f"Mode: RGB\n"
                f"Capacity: {human_size(capacity)}"
            )
            self.status_var.set("Encoded image loaded.")
            self.app.log(f"Loaded encoded image: {image_path.name}")
        except Exception as exc:
            messagebox.showerror("Could not load image", str(exc))

    def decode(self) -> None:
        if self.image is None:
            messagebox.showwarning("Image needed", "Load an encoded image first.")
            return
        try:
            message, encrypted = decode_image(self.image, self.password_var.get(), self.lsb_var.get())
            self._set_text(self.message_box, message)
            self._set_text(self.binary_text, binary_message_preview(message))
            if encrypted and not self.password_var.get():
                self.status_var.set("Encrypted payload shown. Enter the password to decrypt it.")
            else:
                self.status_var.set("Hidden message decoded.")
            self.app.log("Decoded hidden message.")
        except Exception as exc:
            messagebox.showerror("Decoding failed", str(exc))

    def copy_message(self) -> None:
        message = self.message_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(message)
        self.status_var.set("Message copied to clipboard.")

    def export_message(self) -> None:
        self._export_text("decoded_message.txt", self.message_box.get("1.0", "end-1c"))

    def export_binary(self) -> None:
        self._export_text("decoded_binary.txt", self.binary_text.get("1.0", "end-1c"))

    def _export_text(self, default_name: str, content: str) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_name, filetypes=[("Text", "*.txt")])
        if not path:
            return
        Path(path).write_text(content, encoding="utf-8")
        self.status_var.set(f"Exported {Path(path).name}")
        self.app.log(f"Exported {Path(path).name}")

    def _show_image(self, image: Image.Image) -> None:
        preview = image.copy()
        preview.thumbnail((500, 420))
        self.preview_ref = ImageTk.PhotoImage(preview)
        self.preview.configure(image=self.preview_ref, text="")

    def _set_text(self, box, text: str) -> None:
        box.delete("1.0", "end")
        box.insert("1.0", text)

    def append_log(self, line: str) -> None:
        if hasattr(self, "log_text"):
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
