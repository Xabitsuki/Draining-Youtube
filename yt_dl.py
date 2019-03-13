from __future__ import unicode_literals
import youtube_dl


def yt_dl(url, opts={}):

    if not opts:
        # Provide an output template to store all the videos in a single directory,
        # name them by id and extension and write information in json file
        opts = {#'format': '(mp4)',
                'outtmpl': 'videos/%(id)s/%(id)s_%(resolution)s.%(ext)s',
                'writeinfojson': 'videos/%(id)s/'}

    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])


if __name__ == '__main__':

    url = 'https://www.youtube.com/watch?v=R3AKlscrjmQ'

    yt_dl(url=url)
