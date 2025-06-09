# pyspotlightarchiver

**pyspotlightarchiver** is a Python CLI tool for fetching, preserving, and managing Windows Spotlight images.

Inspired by [Spotlight-Downloader](https://github.com/ORelio/Spotlight-Downloader).

## 🚀 Features

- List available Spotlight image URLs
- Download Spotlight images in 1080p or 4K resolution
- Filter by locale and orientation
- Embed EXIF metadata with `exiftool`
- Avoid duplicate downloads with perceptual hash and URL checks
- Automatic throttling to avoid rate limits

## 📦 Requirements

- Python 3.10 or higher ([Download Python](https://www.python.org/downloads/))
- [`exiftool`](https://exiftool.org/) (optional, required for `--embed-exif`)

## ⚖️ Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yell0wsuit/pyspotlightarchiver.git
   cd pyspotlightarchiver
   ```

   Or [download as ZIP](https://github.com/yell0wsuit/pyspotlightarchiver/archive/refs/heads/main.zip) and extract it.

2. **(Optional) Create a virtual environment:**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

   We recommend using a virtual environment to avoid conflicts with other Python packages.

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Usage

Run the tool using:

```bash
python ./src/main.py [command] [options]
```

### Available commands

#### `list-url`

List available Windows Spotlight image URLs.

```bash
python ./src/main.py list-url [options]
```

| Option         | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `--api-ver`    | API version to use (`3` for 1080p, `4` for 4K). Default: `3`.               |
| `--locale`     | Locale code (e.g., `en-us`). Use `all` to include all locales. Default: `en-us`. |
| `--orientation`| Filter by image orientation: `landscape`, `portrait`, or `both`. Default: `landscape`. |
| `--verbose`    | Enable verbose output.                                                      |

#### `download`

Download Spotlight images to your computer.

```bash
python ./src/main.py download --single|--multiple [options]
```

**Required**:

- `--single`: Download a single image.
  - If `--locale all`, a random locale is selected.
  - If `--orientation both`, both orientations are downloaded.

- `--multiple`: Download all available images.
  - With `--locale all`, all locales are processed.
  - With `--orientation both`, both versions are downloaded.

**Additional Options**:

| Option            | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `--api-ver`       | API version (`3` or `4`). Default: `3`.                                     |
| `--locale`        | Locale code (e.g., `en-us`). Default: `en-us`.                              |
| `--orientation`   | Image orientation: `landscape`, `portrait`, or `both`. Default: `landscape`. |
| `--save-dir`      | Directory to save downloaded images. Default: `downloaded_spotlight`.       |
| `--embed-exif`    | Embed EXIF metadata using `exiftool`.                                       |
| `--exiftool-path` | Path to `exiftool`. Required if not in system `PATH`.                       |
| `--verbose`       | Show detailed logs.                                                         |

## 📌 Notes

### 🔄 Locale throttling

When using `--locale all`, the tool throttles API requests to avoid rate limits.

- Locales are processed in chunks of 15.
- Delay increases after each chunk:
  - After 15 locales: wait 5 sec
  - After 30: wait 10 sec
  - After 45: wait 15 sec
  - ...up to a maximum of 180 seconds.

### 🔁 Download loop (with `--multiple`)

The tool continues downloading images until:

- No new images are found after 5 consecutive attempts, or
- A maximum of 100 download attempts is reached.

Delay increases gradually after every 5 attempts, capped at 180 seconds to avoid rate limiting.

### 📂 Caching & duplicates

- A local SQLite database tracks downloaded image URLs and perceptual hashes
- Located at: `.cache/downloaded_images.sqlite`
- Prevents redownloading of identical images.
- Detected perceptual duplicates are logged in: `phash_duplicates_report.md`

💡 **Tip**: Do not delete the cache database to preserve download history.

## 📄 License

This project is licensed under the [GNU GPLv3](LICENSE).
