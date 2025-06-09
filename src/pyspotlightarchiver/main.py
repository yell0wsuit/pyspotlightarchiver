"""Main module for the pyspotlightarchiver tool"""

import argparse
from pyspotlightarchiver.utils.list_url import list_url  # pylint: disable=import-error
from pyspotlightarchiver.utils.download_utils import (  # pylint: disable=import-error
    download_single,
    download_multiple_until_exhausted,
)
from pyspotlightarchiver.helpers.download_db import init_db  # pylint: disable=import-error


def main():
    """Main function to parse arguments and call the appropriate function"""
    parser = argparse.ArgumentParser(
        description=(
            "pyspotlightarchiver by yell0wsuit\n"
            "A tool to archive, manage and preserve Windows Spotlight images.\n"
            "GitHub: https://github.com/yell0wsuit/pyspotlightarchiver"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparser_map = {}

    # List-url subcommand
    list_parser = subparsers.add_parser(
        "list-url",
        help="List available Spotlight pictures URLs.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparser_map["list-url"] = list_parser
    list_parser.add_argument(
        "--api-ver",
        type=int,
        choices=[3, 4],
        default=3,
        help="API version to use ('3' or '4'). Default: 3",
    )
    list_parser.add_argument(
        "--locale",
        type=str,
        default="en-us",
        help="Locale code (e.g., 'en-us'). Use 'all' to include all available locales. Default: 'en-us'",
    )
    list_parser.add_argument(
        "--orientation",
        type=str,
        choices=["landscape", "portrait", "both"],
        default="landscape",
        help="Image orientation to filter: 'landscape', 'portrait', or 'both'. Default: 'landscape'",
    )
    list_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output. Default: false",
    )

    # Download subcommand
    download_parser = subparsers.add_parser(
        "download",
        help="Download Spotlight pictures to your computer.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparser_map["download"] = download_parser
    group = download_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--single",
        action="store_true",
        help="Download a single image.\n"
        "If --locale is 'all', a random image is chosen from one of the available locales.\n"
        "If --orientation is 'both', both versions will be downloaded.\n"
        "Only one of --single or --multiple can be used.",
    )
    group.add_argument(
        "--multiple",
        action="store_true",
        help="Download multiple images.\n"
        "If --locale is 'all', every image from every locale is downloaded.\n"
        "If --orientation is 'both', both versions are downloaded.\n"
        "Only one of --single or --multiple can be used.",
    )
    download_parser.add_argument(
        "--api-ver",
        type=int,
        choices=[3, 4],
        default=3,
        help="API version to use ('3' or '4'). Default: 3",
    )
    download_parser.add_argument(
        "--locale",
        type=str,
        default="en-us",
        help="Locale code (e.g. 'en-us'). Default: 'en-us'",
    )
    download_parser.add_argument(
        "--orientation",
        type=str,
        choices=["landscape", "portrait", "both"],
        default="landscape",
        help="Image orientation: 'landscape', 'portrait', or 'both'. Default: 'landscape'",
    )
    download_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output. Default: false",
    )
    download_parser.add_argument(
        "--save-dir",
        type=str,
        help="Directory to save the images. Default: 'downloaded_spotlight' in the current working directory",
    )
    download_parser.add_argument(
        "--embed-exif",
        action="store_true",
        help="Embed EXIF metadata in the images. Default: false",
    )
    download_parser.add_argument(
        "--exiftool-path",
        type=str,
        help="Path to the exiftool executable. Default: using the PATH environment variable",
    )

    args = parser.parse_args()

    if args.command == "download" and args.locale.lower() == "all":
        if args.embed_exif:
            print(
                "Warning: When --locale is 'all', --embed-exif is automatically set to false."
            )
            args.embed_exif = False

    if args.command == "list-url":
        list_url(args.api_ver, args.locale, args.orientation, args.verbose)
    elif args.command == "download":
        if args.single:
            init_db(args.save_dir)
            download_single(
                args.api_ver,
                args.locale,
                args.orientation,
                args.verbose,
                args.save_dir,
                args.embed_exif,
                args.exiftool_path,
            )
        elif args.multiple:
            init_db(args.save_dir)
            download_multiple_until_exhausted(
                args.api_ver,
                args.locale,
                args.orientation,
                args.verbose,
                args.save_dir,
                args.embed_exif,
                args.exiftool_path,
            )
    else:
        parser.print_help()
        print("\nAvailable Commands:\n")
        for subparser_name, subparser in subparser_map.items():
            print(f"Command '{subparser_name}':")
            print(subparser.format_help())
            print("-" * 40 + "\n")


if __name__ == "__main__":
    main()
