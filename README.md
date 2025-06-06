# pyspotlightarchiver

pyspotlightarchiver, a CLI tool written in Python to fetch, preserve and manage Windows Spotlight images.

Inspired by [Spotlight-Downloader](https://github.com/ORelio/Spotlight-Downloader).

## Features

- List available Spotlight pictures URLs.
- Download Spotlight pictures to your computer.

## Requirements

- Python 3.10 or higher. Install from [official website](https://www.python.org/downloads/).

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/yell0wsuit/pyspotlightarchiver.git
   cd pyspotlightarchiver
   ```

You can also [download the repository as a zip file](https://github.com/yell0wsuit/pyspotlightarchiver/archive/refs/heads/main.zip) and extract it.

2. **(Optional) Create a virtual environment:**

   ```
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

## Usage

Run the tool from the command line:

```
python ./src/main.py [options]
```

### Options

| Command | Description |
|---------|-------------|
| `download` | Download Spotlight pictures to your computer. |
| `list-url` | List available Spotlight pictures URLs. |

| Subcommand | Description |
|------------|-------------|
| `--single` | <strong>Only for `download` command.</strong><br>Download a single image.<br>If `--locale` is `all`, a random image is chosen from one of the available locales.<br>If `--orientation` is `both`, both versions are downloaded. |
| `--multiple` | <strong>Only for `download` command.</strong><br>Download multiple images.<br>If `--locale` is `all`, every image from every locale is downloaded.<br>If `--orientation` is `both`, both versions are downloaded. |
| `--api-ver` | API version to use. |
| `--locale` | Locale code to use. Format: `en-us`. Use `all` to include all available locales. |
| `--orientation` | Image orientation to filter. Format: `landscape`, `portrait`, `both`. |
| `--verbose` | Verbose output. |

## Notes

- When you use the `--locale all` option, the tool automatically throttles API requests to help prevent rate limiting. Locales are processed in chunks of 15. After each chunk, the tool waits for a delay calculated as:

  `delay = 10 * current chunk number`

  For example:

  - After the first 15 locales, it waits 10 seconds.
  - After the next 15, it waits 20 seconds.
  - After the third chunk, it waits 30 seconds.
  - ...and so on.

  This approach helps avoid sending too many requests in a short period and reduces the risk of hitting API rate limits.

  Use the `--verbose` option to see the delay in action.

## License

This tool is licensed under the GPL-3.0 license. See [the LICENSE file](LICENSE) for more details.
