from __future__ import unicode_literals
import youtube_dl
import os
import time
import json


class Timer:

    def __init__(self):
        self.time = 0

    def start(self):
        self.time = time.time()

    def stop(self, print_flag=True):
        self.time = time.time() - self.time

        pretty_time = time.strftime("%H:%M:%S", time.gmtime(self.time))
        if print_flag: print('\nExecution time : {}\n'.format(pretty_time))


def yt_dl(url, opts={}):
    """Call youtube-dl to download a video providing the url"""

    if not opts:
        # Provide an output template to store all the videos in a single directory,
        # name them by id and extension and write information in json file
        opts = {'outtmpl': 'videos/%(id)s/%(id)s_%(resolution)s.%(ext)s',
                'writeinfojson': 'videos/%(id)s/'}

    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])

def path_to_vid_dir(vid_id):
    """2returns full path to video dir assuming call from main folder"""

    return os.path.join(os.getcwd(), 'videos', vid_id)


def path_to_vid_file(vid_id, vid_format):
    """returns full path to video file assuming call from main folder"""

    # search for file in path
    path = path_to_vid_dir(vid_id=vid_id)

    # Look for file matching the format
    vid_file = [el for el in os.listdir(path) if el.endswith(vid_format)][0]  # TODO: should throw error if no file

    return os.path.join(path_to_vid_dir(vid_id), vid_file)


def get_dic_info(vid_id):
    """Load the info dictionnary created by youtube-dl when the video was downloaded."""

    path_dir = path_to_vid_dir(vid_id=vid_id)
    list_ = [el for el in os.listdir(path_dir) if el.endswith('.info.json')]
    path_info = os.path.join(path_dir, list_[0])

    with open(path_info) as f:
        dic_info = json.load(f)

    return dic_info


def vid_xtrct(vid_id, vid_format, start=0, stop=30):
    """creates a copy of the video that begins at start (in seconds) parameter and ends at ends at stop (in seconds)
    parameter"""

    start = time.strftime("%H:%M:%S", time.gmtime(start))
    stop = time.strftime("%H:%M:%S", time.gmtime(stop))

    split = path_to_vid_file(vid_id=vid_id, vid_format=vid_format).split(sep='.', maxsplit=1)

    path_to_trim_file = '{}-{}-{}.{}'.format(split[0], start, stop, split[1])

    cmd_str = 'avconv -i {} -s {} -t {} -codec copy {}'.format(path_to_vid_file(vid_id=vid_id, vid_format=vid_format),
                                                               start,
                                                               stop,
                                                               path_to_trim_file)
    os.system(cmd_str)


def frame_xtrct(vid_id, vid_format, imgs_per_sec=2):

    """ Creates a directory that contains the frames the extracted frames and extracts the frames calling avconv"""

    path_vid_dir = path_to_vid_dir(vid_id)
    path_frames_dir = os.path.join(path_vid_dir, 'frames')

    # Create "frame" directory:
    if not os.path.isdir(path_frames_dir):
        os.mkdir(path_frames_dir)

    # Extract frames using specified rate and format
    path_file = path_to_vid_file(vid_id=vid_id, vid_format=vid_format)

    cmd_str = 'avconv -i {} -r {} -f image2 {}/frame%04d.png'.format(path_file,
                                                                     imgs_per_sec,
                                                                     path_frames_dir)
    os.system(cmd_str)


def remove_ds_store(path):

    """Remove .DS_Store file"""
    path_ds_store = '{}/.DS_Store'.format(path)

    if os.path.isfile(path_ds_store):
        os.remove(path_ds_store)


def image_list(vid_id, image_directory='frames', out_directory='out_openMVG'):
    """Calls openMVG for to perform the image listing"""

    # Get the width of the frames by searching into dictionary of information
    width = get_dic_info(vid_id=vid_id)['width']

    path_vid_dir = path_to_vid_dir(vid_id=vid_id)
    path_image_directory = os.path.join(path_vid_dir, image_directory)
    path_out_directory = os.path.join(path_vid_dir, out_directory)

    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(path_image_directory,
                                                                       path_out_directory,
                                                                       width)

    os.system(command=cmd)


def image_features(vid_id, sfm_file='sfm_data.json', out_directory='out_openMVG'):
    """Calls openMVG to do compute features"""

    path_sfm = os.path.join(path_to_vid_dir(vid_id), 'out_openMVG', sfm_file)
    cmd = 'openMVG_main_ComputeFeatures - i {} -o {}'.format(path_sfm, out_directory)
    os.system(cmd)
