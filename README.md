# pyspotlightarchiver

pyspotlightarchiver, a CLI tool written in Python to fetch, preserve and manage Windows Spotlight images.

Inspired by [Spotlight-Downloader](https://github.com/ORelio/Spotlight-Downloader).

## Features

- List available Spotlight pictures URLs.
- Download Spotlight pictures to your computer.

## Requirements

- (Tested on) Python 3.10 or higher. Install from [official website](https://www.python.org/downloads/).
- [exiftool](https://exiftool.org/) to embed EXIF metadata in the images.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yell0wsuit/pyspotlightarchiver.git
   cd pyspotlightarchiver
   ```

   You can also [download the repository as a zip file](https://github.com/yell0wsuit/pyspotlightarchiver/archive/refs/heads/main.zip) and extract it.

2. **(Optional) Create a virtual environment:**

   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the tool from the command line:

```bash
python ./src/main.py [options]
```

- For listing available Spotlight pictures URLs, use the `list-url` command.
- For downloading as many Spotlight pictures as possible to your computer, use the `download` command.
  - 4K images: `download --api-ver 4 --multiple --embed-exif`
  - 1080p images: `download --api-ver 3 --multiple --embed-exif`
  - You can add `--locale all` to download images from all available locales.

### Options

| Command | Description |
|---------|-------------|
| `download` | Download Spotlight pictures to your computer. |
| `list-url` | List available Spotlight pictures URLs. |

| Subcommand | Description |
|------------|-------------|
| `--single` | <strong>Only for `download` command.</strong><br>Download a single image.<br>If `--locale` is `all`, a random image is chosen from one of the available locales.<br>If `--orientation` is `both`, both versions are downloaded. |
| `--multiple` | <strong>Only for `download` command.</strong><br>Download multiple images.<br>If `--locale` is `all`, every image from every locale is downloaded.<br>If `--orientation` is `both`, both versions are downloaded. |
| `--save-dir` | <strong>Only for `download` command.</strong><br>Directory to save the images. Default: `downloaded_spotlight` in the current working directory. |
| `--api-ver` | API version to use. |
| `--locale` | Locale code to use. Format: `en-us`. Use `all` to include all available locales. |
| `--orientation` | Image orientation to filter. Format: `landscape`, `portrait`, `both`. |
| `--save-dir` | <strong>Only for `download` command.</strong><br>Directory to save the images. Default: `downloaded_spotlight` in the current working directory. |
| `--embed-exif` | <strong>Only for `download` command.</strong><br>Embed EXIF metadata in the images using [exiftool](https://exiftool.org/). Default: false. |
| `--exiftool-path` | <strong>Only for `download` command.</strong><br>Path to the exiftool executable. Default: using the PATH environment variable. |
| `--verbose` | Verbose output. |

## Notes

- When you use the `--locale all` option, the tool automatically throttles API requests to help prevent rate limiting. Locales are processed in chunks of 15. After each chunk, the tool waits for a delay calculated as:

  `delay = 5 * current chunk number`

  For example:

  - After the first 15 locales, it waits 5 seconds.
  - After the next 15, it waits 10 seconds.
  - After the third chunk, it waits 15 seconds.
  - ...and so on.

  The delay is capped at 180 seconds to prevent excessive waiting while balancing the rate limit. This strategy minimizes the number of requests sent in a short timeframe, thereby lowering the chance of exceeding API rate limits.

- Once images are downloaded, the tool records their URLs and perceptual hashes in a SQLite database.
  - This database is located at `.cache/downloaded_images.sqlite` in the current working directory.
  - It helps prevent the re-downloading of identical images.
  - Additionally, it identifies potential duplicates and logs them in the `phash_duplicates_report.md` file in the current working directory.

## License

This tool is licensed under the GPL-3.0 license. See [the LICENSE file](LICENSE) for more details.
