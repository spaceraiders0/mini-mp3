#!/usr/bin/python

"""The video downloader.
"""

import sys
import shutil
import pytube
import subprocess
import definitions
from pathlib import Path
from logger import Logger
from argparse import ArgumentParser
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parents[1]
SERVER_LOGGER = Logger("%N %L @ %T", output_directory=ROOT_DIR / Path("logs"))
last_size = 0

parser = ArgumentParser(description="""A small script that wraps around Pytube
                        to download YouTube videos.""")
parser.add_argument("source", help="""The video(s) or Playlist(s) to download
                    from.""", nargs="*")
parser.add_argument("-o", "--output", help="The directory to output to.",
                    default=".")
parser.add_argument("-f", "--format", help="The format to convert to.")
parser.add_argument("-se", "--silent-errors", help="""Makes the output of
                    errors silent""", action="store_true")
parser.add_argument("-sp", "--silent-prog", help="""Makes the output of the
                    progress bar silent.""", action="store_true")
parser.add_argument("-k", "--keep", help="""Keeps both the original and
                    converted files.""", action="store_true")
parsed_args = parser.parse_args()

OUTPUT_DIR = Path(parsed_args.output)

# Make sure the output directory provided exists.
if not OUTPUT_DIR.exists():
    if not parsed_args.silent_errors:
        print(f"Path '{str(OUTPUT_DIR)}' doesn't exist.")

    sys.exit(0)

# Make sure ffmpeg is installed if they wish to convert.
if shutil.which("ffmpeg") is None and parsed_args.format is not None:
    if not parsed_args.silent_errors:
        print("Could not find ffmpeg! You must install it before converting.")

    sys.exit(0)

for source in definitions.get_urls(parsed_args.source, parsed_args.silent_errors):
    try:
        # Whether or not to display output.
        if not parsed_args.silent_prog:
            video_source = pytube.YouTube(source,
                                  on_progress_callback=definitions.on_progress,
                                  on_complete_callback=definitions.on_complete)
        else:
            video_source = pytube.YouTube(source)

        file_path = Path(video_source.streams.first().download(output_path=str(OUTPUT_DIR))).absolute()
        file_dir = file_path.stem
        out_dir = OUTPUT_DIR / Path(file_path.stem) 
        
        
        # Convert the video if the user prompted for conversion.
        if parsed_args.format is not None:
            subprocess.run(["ffmpeg", "-loglevel", "warning", "-i",
                           f"{file_dir}.mp4", f"{out_dir}.{parsed_args.format}"])

            # Remove the source file if requested.
            if not parsed_args.keep:
                file_path.unlink()

    except pytube.exceptions.VideoPrivate:
        if not parsed_args.silent_errors:
            print(f"{source} is a private video.")
    except pytube.exceptions.VideoPrivate:
        if not parsed_args.silent_errors:
            print(f"{source} is deleted.")
    except pytube.exceptions.RegexMatchError:
        if not parsed_args.silent_errors:
            print(f"{source} has invalid regex.")
    except pytube.exceptions.VideoUnavailable:
        if not parsed_args.silent_errors:
            print(f"{source} is an unavailable video.")
    except Exception:
        print(f"Unknown error occured on URL {source}")


