"""Some functions defined for mini-mp3.py
"""

import textwrap
import pytube
from colorama import init, Fore

init(autoreset=True)

TITLE_COLOR = Fore.RED
PERCENT_COLOR = Fore.YELLOW
last_size = 0


def get_urls(source: list, silent_errors=False) -> list:
    """Returns a list of all URLs of both regular videos, and
    URLs from Playlists inside the list.

    :param source: the URLs to extract
    :type source: list

    :return: the URLs that were extracted
    :rtype: list
    """

    video_urls = [*source]

    # Fill up source_urls and add videos from Playlists.
    while len(video_urls) > 0:
        url = video_urls.pop(0)

        # This is the signature of a Playlist
        if "youtube.com/playlist?list=" in url:
            try:
                video_urls += pytube.Playlist(url)
            except pytube.exceptions.RegexMatchError:
                if not silent_errors:
                    print(f"Invalid regex for URL {url}")
        else:
            yield url


def on_progress(stream: pytube.Stream, v_bytes: bytes, remaining: int = 0):
    """The callback for when the Video downloaded has progressed.

    :param stream: the video stream object
    :type stream: pytube.Stream

    :param v_bytes: the bytes of the video's mp4
    :type v_bytes: bytes

    :param remaining: the number of bytes left to download
    :type remaining: int
    """

    global last_size

    if last_size == 0:
        last_size = remaining
 
    percent_completed = round(100 - (remaining / last_size) * 100, 2)
    print(f"{TITLE_COLOR}[{stream.title}] - {PERCENT_COLOR}{percent_completed}%", end="\r")


def on_complete(x, y):
    """The callback for when the video has completed downloading.
    """

    global last_size

    last_size = 0
    print("")

