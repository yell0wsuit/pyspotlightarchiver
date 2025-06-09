"""Module to set EXIF metadata using exiftool."""

import subprocess
import shutil
import os
import platform
import tempfile


def _exiftool_exists(exiftool_path=None):
    if exiftool_path:
        # If a directory is provided, look for exiftool executable inside it
        if os.path.isdir(exiftool_path):
            # Check for common exiftool executable names across platforms
            system = platform.system()
            if system == "Windows":
                possible_names = ["exiftool.exe", "exiftool(-k).exe", "exiftool"]
            else:  # macOS (Darwin) and Linux
                possible_names = ["exiftool"]

            for name in possible_names:
                full_path = os.path.join(exiftool_path, name)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
            return None
        # If a file path is provided, check if it exists and is executable
        elif os.path.isfile(exiftool_path) and os.access(exiftool_path, os.X_OK):
            return exiftool_path
        else:
            return None
    # Fall back to checking if exiftool is in PATH
    return shutil.which("exiftool")


def set_exif_metadata_exiftool(
    image_path,
    title=None,
    copyright_text=None,
    caption_title=None,
    caption_description=None,
    exiftool_path=None,
    verbose=False,
):
    """Method to set EXIF metadata using exiftool.
    Args:
        image_path (str): The path to the image file.
        title (str): The title of the image.
        copyright_text (str): The copyright text of the image.
        caption_title (str): The title of the caption (v4 only). Stored as comment.
        caption_description (str): The description of the caption (v4 only). Stored as comment.
        exiftool_path (str): The path to the exiftool executable or directory containing it.
    """
    exiftool_cmd = _exiftool_exists(exiftool_path)

    if not exiftool_cmd:
        if exiftool_path:
            print(
                f"ExifTool cannot be found at '{exiftool_path}'. Please check the path or install it from https://exiftool.org/"
            )
        else:
            print(
                "ExifTool cannot be found. Please install it from https://exiftool.org/, or specify the path with --exiftool-path."
            )
        return

    args = [exiftool_cmd, "-overwrite_original", "-charset", "utf8"]
    if title:
        args.append(f"-ImageDescription={title}")
        if verbose:
            print(f"Title: {title}")
    if copyright_text:
        args.append(f"-Copyright={copyright_text}")
        if verbose:
            print(f"Copyright: {copyright_text}")
    if caption_title or caption_description:
        comment = ""
        if caption_title:
            comment += f"Title: {caption_title}"
        if caption_description:
            if comment:
                comment += "\n\n"
            comment += f"Description: {caption_description}"

        # Write comment to a temporary file (UTF-8 encoding)
        with tempfile.NamedTemporaryFile(
            "w", delete=False, encoding="utf-8", suffix=".txt"
        ) as tf:
            tf.write(comment)
            temp_comment_path = tf.name

        args.append(f"-UserComment<={temp_comment_path}")
        args.append(f"-XPComment<={temp_comment_path}")
        if verbose:
            print(f"Comment: {comment}")
    else:
        temp_comment_path = None

    args.append(image_path)

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        if verbose:
            print(
                f"EXIF metadata written to {image_path} using exiftool. Output: {result.stdout}"
            )
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"ExifTool error: {e.stderr}")
    except Exception as e:
        print(f"Error running exiftool: {e}")
