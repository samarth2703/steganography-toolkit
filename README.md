# Steganography Toolkit

Steganography Toolkit is an interactive Python desktop application for hiding and revealing secret messages inside images using Least Significant Bit steganography.

It is built as a cybersecurity learning tool, not just a simple encoder and decoder. The app helps users understand how hidden data changes image pixels through visual comparison, binary previews, bit-plane inspection, and pixel-level analysis.

## Features

- Hide secret text inside PNG and BMP images
- Decode hidden messages from encoded images
- Optional password protection using Fernet encryption
- Choose 1, 2, or 3 LSB depth
- Automatic image capacity checking
- Image metadata viewer
- Binary message viewer
- Bit-change visualizer
- Pixel inspector
- Original vs encoded image comparison
- Exaggerated difference image viewer
- Bit-plane viewer
- Quality metrics including MSE and PSNR
- Export encoded images, decoded messages, binary data, and logs
- Dark CustomTkinter interface

## Tech Stack

- Python
- CustomTkinter
- Pillow
- NumPy
- Cryptography
- PyInstaller

## Project Structure

```text
Steganography Toolkit/
├── app.py
├── requirements.txt
├── build_exe.bat
├── build_exe.ps1
├── core/
│   ├── bit_utils.py
│   ├── crypto.py
│   ├── decoder.py
│   ├── encoder.py
│   ├── validator.py
│   └── visualizer.py
├── gui/
│   ├── compare_window.py
│   ├── decode_tab.py
│   ├── encode_tab.py
│   ├── main_window.py
│   └── settings.py
├── assets/
│   └── st.ico
├── input/
└── output/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/steganography-toolkit.git
cd steganography-toolkit
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

## How To Use

1. Open the Encode tab.
2. Upload a PNG or BMP image.
3. Enter the secret message.
4. Optionally enter a password.
5. Select the LSB depth.
6. Click Encode Message.
7. Save the encoded image.
8. Open the Decode tab.
9. Load the encoded image.
10. Enter the password if the message was encrypted.
11. Decode and export the message.

## Build EXE

Place your icon at:

```text
assets/st.ico
```

Then run:

```powershell
.\build_exe.ps1
```

Or double-click:

```text
build_exe.bat
```

The executable will be created at:

```text
dist/SteganographyToolkit.exe
```

## Cybersecurity Concepts Demonstrated

- Image steganography
- Least Significant Bit encoding
- Binary data handling
- Pixel-level image processing
- Symmetric encryption
- Capacity validation
- Secure message extraction
- GUI-based cybersecurity tooling

## Disclaimer

This project is created for educational and portfolio purposes. Use it responsibly and only with images and data you own or have permission to modify.
