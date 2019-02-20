import os


def youtube_dl(url, options=''):
    """function used to invok youtube-dl"""
    cmd = 'youtube-dl'
    if options:
        str = '{} {} {}'.format(cmd, options, url)
    else:
        str = '{} {}'.format(cmd, url)
    os.system(str)


if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=ksFistAg12I&frags=pl%2Cwn'
    youtube_dl(url=url)
