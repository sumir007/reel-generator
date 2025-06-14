# 🎞️ Reel Generator

A Python tool to convert downloaded 9GAG videos into Instagram Reels or YouTube Shorts format (9:16) by:

* Resizing and padding the video (without cropping)
* Adding a low-volume lofi background music
* Exporting them as `.mp4` videos ready for social media

---

## 📦 Features

* Automatically finds and processes the latest download folder (`run_*`)
* Resizes non-vertical videos and pads them to fit 1080x1920 (9:16)
* Overlays background music (`no-copyright-music-lofi-330213.mp3`)
* Skips already vertical videos when appropriate
* Batch processes all `.mp4` and `.webm` videos in the folder

---

## 🚀 Installation

### 1. Clone this repository

```bash
git clone https://github.com/sumir007/reel-generator.git
cd reel-generator
```

### 2. Create a Python virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate    # On macOS/Linux
venv\Scripts\activate       # On Windows
```

### 3. Install Python dependencies

Only `ffmpeg-python` is required:

```bash
pip install ffmpeg-python
```

> 🔧 If you encounter `ModuleNotFoundError: No module named 'ffmpeg'`, make sure you're using the right Python environment.

### 4. Install FFmpeg (Required)

* **Windows:** Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add to your `PATH`
* **macOS:** Use Homebrew: `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

To verify:

```bash
ffmpeg -version
```

If this doesn't work:

* Make sure it's correctly added to your system `PATH`
* Try restarting your terminal or system

---

## 🛠️ How to Run

### 1. Structure your folders like this:

```
reel-generator/
├── run_2025-06-04/
│   ├── video1.mp4
│   ├── video2.webm
│   └── ...
├── no-copyright-music-lofi-330213.mp3
├── reel_generator.py
```

> 🗂️ Make sure the folder with videos is named like `run_YYYY-MM-DD` (or starts with `run_`).

### 2. Run the script

```bash
python reel_generator.py
```

The converted videos will be saved in:

```
E:/ReelGenerator/Output
```

(or the folder you define, see below 👇)

---

## ⚙️ How to Customize Paths

Open `reel_generator.py` and scroll to the bottom:

```python
# Change this to wherever your 9gag downloads are
base_download_dir = "E:/ReelGenerator/9gag_downloads"

# Change this to where you want the converted reels saved
output_folder = "E:/ReelGenerator/Output"

# Path to the background music file (already in repo)
background_music = "no-copyright-music-lofi-330213.mp3"
```

Replace these with your actual folder paths.

---

## ❌ Common Errors & Fixes

### ⚠️ `ffmpeg` not recognized

> `ffmpeg: command not found` or `'ffmpeg' is not recognized as an internal or external command`

**Fix:**
Make sure `ffmpeg` is installed and added to your `PATH`. Restart your terminal or system if needed.

---

### ⚠️ `ModuleNotFoundError: No module named 'ffmpeg'`

**Fix:**
Install the Python module:

```bash
pip install ffmpeg-python
```

---

### ⚠️ `subprocess.CalledProcessError`

**Fix:**
This often means the FFmpeg command failed. Scroll up in the console to find the detailed error.

Common cause:

* Input video resolution breaks scaling/padding logic.
* `no-copyright-music-lofi-330213.mp3` file is missing or renamed.

Double-check:

* Video dimensions
* File paths and names
* That FFmpeg works from terminal

---

## 🔪 Sample Output

The output videos will be in 1080x1920 format, like this:

* Original: `460x564` → Scaled and padded to `1080x1920`
* Music: Low-volume background
* Output: `reel_video1.mp4`, `reel_video2.mp4`, etc.

---

## 📅 How to Download and Use From GitHub

If you want to run this on another machine:

```bash
git clone https://github.com/sumir007/reel-generator.git
cd reel-generator
pip install ffmpeg-python
python reel_generator.py
```

Make sure:

* FFmpeg is installed and on your PATH
* Your input folder is named `run_*` and placed properly
* The background music is present in the repo base

---

## 🙏 Credits

Background music: \[lofi track used is free to use with no copyright]

Made by [sumir007](https://github.com/sumir007)
