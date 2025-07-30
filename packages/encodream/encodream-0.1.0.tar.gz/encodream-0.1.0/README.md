# 🧠 encodream

> Encoding Playground of Dreams: ASCII art, UTF-8 tools, machine code converter, and visualization playground in your terminal — powered by 20+ PyPI packages.

---

## ✨ Features (15 Fitur Unggulan)

1. 🎨 **ASCII Art Generator** – Buat teks besar artistik pakai `pyfiglet`
2. 🔢 **UTF-8 Encoder & Decoder** – Ubah string ke bytes, binary, hex, int
3. 🧮 **Machine Code Viewer** – Lihat dump hex seperti mesin
4. 💧 **Binary Highlighter** – Tampilkan bit per karakter secara visual
5. 📈 **Byte Visualizer** – Visualisasi nilai byte dalam chart `matplotlib`
6. 🧾 **ASCII Table** ala Arduino – Tampilkan nilai ASCII: int, hex, bin
7. 🎭 **Regex Search** – Cari teks dengan pola regex `re`
8. 🌐 **URL Validator** – Validasi format URL `validators`
9. 📋 **Clipboard Integration** – Copy teks langsung ke clipboard `pyperclip`
10. 🔤 **Transliterator** – Ubah Unicode → ASCII `unidecode`
11. 🌍 **Fake Profile Generator** – Data palsu realistis `faker`
12. ✨ **Terminal Animation** – ASCII animasi seperti `ascii.live`
13. 📝 **Markdownify** – Konversi HTML → Markdown `markdownify`
14. 💾 **File System Tool** – Gunakan `pathlib` untuk cari file, save art
15. 🔧 **CLI & Spinner** – Progress bar, animasi loading (`tqdm`, `yaspin`, `rich`)

---

## 🚀 Installation

```bash
pip install encodream
```

Requires Python 3.7+

⚙️ Usage
▶️ Full Demo
```bash
python -m encodream "encodream" --demo
```

🧩 Import in Python
```python

from encodream.core import *

ascii_art("PYTHON")

utf8_encode("hello")        # b'hello'
string_to_binary("abc")     # '01100001 01100010 01100011'
machine_code_dump("Hi!")    # '48 69 21'

plot_string_bytes("ASCII")
display_ascii_table("arduino")
```

🎥 Example: Terminal Live ASCII Animation
```python

animated_ascii_terminal(
    texts=["encodream", "UTF-8", "ART", "PYTHON"],
    delay=0.3,
    repeat=15
)
```

📋 Requirements
```txt
numpy
matplotlib
colorama
pyfiglet
pandas
rich
tqdm
click
tabulate
termcolor
chardet
emoji
faker
markdownify
unidecode
humanize
pyperclip
Pillow
validators
```

🧪 Developer Mode
```bash
# Clone and install locally
git clone https://github.com/EdenGithhub/encodream.git
cd encodream
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

🧠 About
Made with ❤️ by [Eden Simamora]
Powerful encoding playground for hackers, makers, educators, and curious minds.

📄 License
MIT © 2025
