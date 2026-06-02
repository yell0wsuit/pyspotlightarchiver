"""Module to set EXIF metadata using Pillow."""

from pathlib import Path

from PIL import ExifTags, Image
from rich import print as rprint

IMAGE_DESCRIPTION = 270
COPYRIGHT = 33432
USER_COMMENT = 37510
XP_COMMENT = 40092


def _build_comment(caption_title=None, caption_description=None):
    comment = ""
    if caption_title:
        comment += f"Title: {caption_title}"
    if caption_description:
        if comment:
            comment += "\n\n"
        comment += f"Description: {caption_description}"
    return comment or None


def _encode_user_comment(comment):
    try:
        return b"ASCII\x00\x00\x00" + comment.encode("ascii")
    except UnicodeEncodeError:
        return b"UNICODE\x00" + comment.encode("utf-16be")


def _encode_xp_comment(comment):
    return comment.encode("utf-16le") + b"\x00\x00"


def set_exif_metadata(
    image_path,
    title=None,
    copyright_text=None,
    caption_title=None,
    caption_description=None,
    verbose=False,
):
    """Set EXIF metadata on an image using Pillow."""
    image_path = Path(image_path)
    comment = _build_comment(caption_title, caption_description)

    try:
        with Image.open(image_path) as image:
            exif = image.getexif()
            if title:
                exif[IMAGE_DESCRIPTION] = title
                if verbose:
                    rprint(f"ℹ️ [gray]LOG: [pillow] Title:[/gray] {title}")
            if copyright_text:
                exif[COPYRIGHT] = copyright_text
                if verbose:
                    rprint(f"ℹ️ [gray]LOG: [pillow] Copyright:[/gray] {copyright_text}")
            if comment:
                exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                exif_ifd[USER_COMMENT] = _encode_user_comment(comment)
                exif[ExifTags.IFD.Exif] = exif_ifd
                exif[XP_COMMENT] = _encode_xp_comment(comment)
                if verbose:
                    rprint(f"ℹ️ [gray]LOG: [pillow] Comment:[/gray] {comment}")

            if image.format == "JPEG":
                image.save(
                    image_path,
                    exif=exif.tobytes(),
                    quality="keep",
                    subsampling="keep",
                )
            else:
                image.save(image_path, exif=exif.tobytes())

        if verbose:
            rprint(
                f"✅ [green]LOG: [pillow] EXIF metadata written to:[/green] {image_path}"
            )
    except Exception as e:  # pylint: disable=broad-exception-caught
        rprint(
            f"❌ [red]LOG: [pillow] Unexpected error ({type(e).__name__}):[/red] {e}"
        )
