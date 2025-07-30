"""
encodream.core - Encoding Playground of Dreams

✨ Fitur:
- ASCII Art (pyfiglet)
- UTF-8 encode/decode ↔ bytes ↔ ints ↔ bin
- Arduino-style representation
- Machine code hex viewer
- Visualisasi byte (matplotlib)
- Colored output (colorama)
- Table formatter (tabulate)
- CLI progress (tqdm, rich)
- Socket simulator encoding
"""
import random
import time
import shutil
import sys
import socket
import pyfiglet
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Style, init as colorama_init
import os
import sys
import re
import chardet  # make sure to install: pip install chardet
from tabulate import tabulate
from tqdm import tqdm
from rich.console import Console
from termcolor import colored
from pathlib import Path
from yaspin import yaspin
import emoji
from faker import Faker
from markdownify import markdownify
from unidecode import unidecode
import humanize
import pyperclip
from PIL import Image
import validators
import uuid

fake = Faker()

colorama_init(autoreset=True)
console = Console()

def ascii_art(text: str, font: str = "slant") -> str:
    """Tampilkan teks sebagai ASCII art dengan pyfiglet"""
    return pyfiglet.figlet_format(text, font=font)


def animated_ascii_terminal(texts=None, delay=0.2, repeat=5):
    """
    Animasi ASCII art di terminal seperti ascii.live

    Parameters:
    - texts: list teks yang akan dianimasikan
    - delay: waktu antar frame
    - repeat: jumlah pengulangan

    Jika texts=None, akan tampil default teks acak.
    """
    if texts is None:
        texts = ["encodream", "encoding", "machine", "ASCII", "PYTHON", "UTF-8"]

    width = shutil.get_terminal_size().columns
    colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE]

    for _ in range(repeat):
        for word in texts:
            art = pyfiglet.figlet_format(word, font=random.choice(["slant", "standard", "3-d", "bulbhead"]))
            lines = art.split("\n")
            color = random.choice(colors)

            # Clear screen (cross-platform)
            print("\033c", end="")  # ANSI escape for clearing screen
            for line in lines:
                centered = line.center(width)
                print(color + centered)
            time.sleep(delay)

def utf8_encode(text: str) -> bytes:
    return text.encode('utf-8')

def utf8_decode(data: bytes) -> str:
    return data.decode('utf-8')

def string_to_binary(text: str) -> str:
    return ' '.join(format(b, '08b') for b in utf8_encode(text))

def string_to_hex(text: str) -> str:
    return ' '.join(format(b, '02x') for b in utf8_encode(text))

def string_to_ints(text: str) -> list:
    return list(utf8_encode(text))

def ints_to_string(lst: list) -> str:
    return bytes(lst).decode('utf-8')

def arduino_ascii_map(text: str) -> list:
    return [{"char": c, "int": ord(c), "hex": hex(ord(c)), "bin": format(ord(c), '08b')} for c in text]

def display_ascii_table(text: str):
    data = arduino_ascii_map(text)
    headers = ["Char", "Dec", "Hex", "Binary"]
    rows = [[d["char"], d["int"], d["hex"], d["bin"]] for d in data]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

def plot_string_bytes(text: str):
    data = string_to_ints(text)
    indices = np.arange(len(data))

    plt.figure(figsize=(10, 4))
    plt.bar(indices, data, color='skyblue')
    plt.xticks(indices, list(text))
    plt.ylabel('Byte Value')
    plt.title(f'Byte Encoding of "{text}"')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def highlight_bytes(text: str):
    print(Fore.GREEN + "Encoded Bytes:")
    for b in utf8_encode(text):
        print(f"{Fore.YELLOW}{b}", end=' ')
    print()


def generate_fake_profile():
    """Generate profil palsu pakai Faker"""
    return fake.simple_profile()

def markdown_from_html(html: str) -> str:
    """Konversi HTML ke Markdown"""
    return markdownify(html)

def transliterate_text(text: str) -> str:
    """Ubah Unicode jadi ASCII terdekat"""
    return unidecode(text)

def human_readable_size(num_bytes: int) -> str:
    """Ubah byte jadi ukuran ramah (KB, MB)"""
    return humanize.naturalsize(num_bytes)

def copy_to_clipboard(text: str):
    """Copy teks ke clipboard"""
    pyperclip.copy(text)

def generate_uuid() -> str:
    """Generate UUID unik"""
    return str(uuid.uuid4())

def is_valid_url(url: str) -> bool:
    """Validasi URL"""
    return validators.url(url)

def ascii_image_preview(image_path: str, width: int = 60) -> str:
    """Konversi gambar ke ASCII preview"""
    try:
        img = Image.open(image_path).convert("L")
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        pixels = img.getdata()
        chars = "@%#*+=-:. "
        ascii_str = ''.join([chars[pixel // 25] for pixel in pixels])
        ascii_img = '\n'.join([ascii_str[i:i+width] for i in range(0, len(ascii_str), width)])
        return ascii_img
    except Exception as e:
        return f"[ERROR] {e}"

def list_files_by_suffix(path: str, suffix: str = ".py") -> list:
    """List semua file dengan ekstensi tertentu pakai pathlib"""
    return [str(p.name) for p in Path(path).glob(f"*{suffix}")]

def show_spinner_demo(text: str):
    """Demo loading spinner"""
    with yaspin(text=f"Processing: {text}", color="cyan") as spinner:
        import time
        time.sleep(2)
        spinner.ok("✅ ")

def print_with_emoji(text: str, emo: str = ":sparkles:"):
    """Print teks dengan emoji"""
    print(emoji.emojize(f"{emo} {text} {emo}", language="alias"))    

def list_font_files(directory: str = "."):
    """Cari semua file .ttf di direktori"""
    return [f for f in os.listdir(directory) if f.lower().endswith(".ttf")]

def regex_search_words(text: str, pattern: str) -> list:
    """Cari semua kata yang cocok dengan pola regex"""
    return re.findall(pattern, text)

def detect_encoding(file_path: str) -> str:
    """Deteksi encoding dari file"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def convert_newlines(text: str, mode: str = "unix") -> str:
    """Konversi newline: unix (\n), windows (\r\n), oldmac (\r)"""
    if mode == "windows":
        return text.replace('\n', '\r\n')
    elif mode == "oldmac":
        return text.replace('\n', '\r')
    return text.replace('\r\n', '\n').replace('\r', '\n')

def is_valid_utf8(byte_data: bytes) -> bool:
    """Cek apakah byte data valid UTF-8"""
    try:
        byte_data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def save_ascii_art_to_file(text: str, filename: str):
    """Generate ASCII art dan simpan ke file"""
    art = ascii_art(text)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(art)

def system_info() -> dict:
    """Ambil informasi sistem"""
    return {
        "platform": sys.platform,
        "os name": os.name,
        "python version": sys.version,
        "cwd": os.getcwd()
    }


def fancy_animation(text: str):
    for c in tqdm(text, desc="Encoding", colour="cyan"):
        console.print(f"[bold magenta]{c}[/bold magenta]", end=" ")
    print()

def socket_simulation(text: str, host="127.0.0.1", port=65432):
    """Simulasi pengiriman data terenkripsi ke server (socket dummy)"""
    encoded = utf8_encode(text)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            s.sendall(encoded)
            data = s.recv(1024)
            print(Fore.GREEN + "Server reply:", data.decode('utf-8'))
        except Exception as e:
            print(Fore.RED + f"Socket Error: {e}")

def binary_visualization(text: str):
    bits = string_to_binary(text).split()
    visual = '\n'.join([f"{Fore.CYAN}{c} → {Fore.YELLOW}{b}" for c, b in zip(text, bits)])
    print(visual)

def License():
    print("""MIT License

Copyright (c) [2025] [Adam Alcander Et Eden Simamora]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")    

def machine_code_dump(text: str):
    hex_view = string_to_hex(text).split()
    print(Fore.MAGENTA + "Machine Code Dump:")
    print(' '.join(hex_view))

def byte_table(text: str):
    bytes_list = utf8_encode(text)
    rows = [[i, b, hex(b), format(b, '08b')] for i, b in enumerate(bytes_list)]
    print(tabulate(rows, headers=["Index", "Byte", "Hex", "Binary"], tablefmt="github"))

def full_demo(text: str):
    print("=" * 60)
    print(ascii_art("encodream", font="standard"))
    print(colored("Original Text:", "cyan"), text)
    print()
    display_ascii_table(text)
    print()
    byte_table(text)
    print()
    highlight_bytes(text)
    binary_visualization(text)
    print()
    plot_string_bytes(text)
    machine_code_dump(text)
    fancy_animation(text)
    print("=" * 60)

# CLI helper
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Encodream Playground")
    parser.add_argument("text", help="Text to encode and analyze")
    parser.add_argument("--demo", action="store_true", help="Run full demo")
    args = parser.parse_args()

    if args.demo:
        full_demo(args.text)
    else:
        print(ascii_art(args.text))

if __name__ == "__main__":
    main()
    print_with_emoji("Welcome to encodream!")
    show_spinner_demo("Encoding magic...")
    print("UUID:", generate_uuid())
    print("Valid URL?", is_valid_url("https://pypi.org"))
    copy_to_clipboard("Hello from encodream!")
    
    print("\nASCII LIVE DEMO (CTRL+C to stop)")
    try:
        animated_ascii_terminal(["encodream", "PYTHON", "UTF-8", "ART!", "💡INNOVATE"], delay=0.4, repeat=10)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    License()    




