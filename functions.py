from __future__ import unicode_literals
import youtube_dl
import os
import time
import json
import numpy as np


class Timer:

    def __init__(self):
        self.time = 0

    def start(self):
        self.time = time.time()

    def stop(self, print_flag=True):
        self.time = time.time() - self.time

        pretty_time = time.strftime("%H:%M:%S", time.gmtime(self.time))
        if print_flag:
            print('\nExecution time : {}\n'.format(pretty_time))


def remove_ds_store(path):

    """Remove .DS_Store file"""
    path_ds_store = '{}/.DS_Store'.format(path)

    if os.path.isfile(path_ds_store):
        os.remove(path_ds_store)


def make_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def pth_vid_dir(vid_id):
    """2returns full path to video dir assuming call from main folder"""

    return os.path.join(os.getcwd(), 'videos', vid_id)


def pth_vid_file(vid_id, vid_format):
    """returns full path to video file assuming call from main folder"""

    # search for file in path
    path = pth_vid_dir(vid_id=vid_id)

    # Look for file matching the format
    vid_file = [el for el in os.listdir(path) if el.endswith(vid_format)][0]  # TODO: should throw error if no file

    return os.path.join(pth_vid_dir(vid_id), vid_file)


# Youtube-dl


def yt_dl(url, opts={}):
    """Call youtube-dl to download a video providing the url"""

    if not opts:
        # Provide an output template to store all the videos in a single directory,
        # name them by id and extension and write information in json file
        opts = {'outtmpl': 'videos/%(id)s/%(id)s_%(resolution)s.%(ext)s',
                'writeinfojson': 'videos/%(id)s/'}

    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])


def get_dic_info(vid_id):
    """Load the info dictionnary created by youtube-dl when the video was downloaded."""

    path_dir = pth_vid_dir(vid_id=vid_id)
    list_ = [el for el in os.listdir(path_dir) if el.endswith('.info.json')]
    path_info = os.path.join(path_dir, list_[0])

    with open(path_info) as f:
        dic_info = json.load(f)

    return dic_info


# Avconv Wrapping

def vid_xtrct(vid_id, vid_format, start=0, stop=30):
    """creates a copy of the video that begins at start (in seconds) parameter and ends at ends at stop (in seconds)
    parameter"""

    start = time.strftime("%H:%M:%S", time.gmtime(start))
    stop = time.strftime("%H:%M:%S", time.gmtime(stop))

    split = pth_vid_file(vid_id=vid_id, vid_format=vid_format).split(sep='.', maxsplit=1)

    path_to_trim_file = '{}-{}-{}.{}'.format(split[0], start, stop, split[1])

    cmd_str = 'avconv -i {} -s {} -t {} -codec copy {}'.format(pth_vid_file(vid_id=vid_id, vid_format=vid_format),
                                                               start,
                                                               stop,
                                                               path_to_trim_file)
    os.system(cmd_str)


def frame_xtrct(vid_id, vid_format, imgs_per_sec=2):

    """ Creates a directory that contains the frames the extracted frames and extracts the frames calling avconv"""

    # Create "frame" directory:
    path_vid_dir = pth_vid_dir(vid_id)
    path_frames_dir = os.path.join(path_vid_dir, 'frames')
    make_dir(path_frames_dir)

    # Extract frames using specified rate and format
    path_file = pth_vid_file(vid_id=vid_id, vid_format=vid_format)

    cmd_str = 'avconv -i {} -r {} -f image2 {}/frame%04d.png'.format(path_file,
                                                                     imgs_per_sec,
                                                                     path_frames_dir)
    os.system(cmd_str)


# OpenMVG wrapping


def openmvg_list(vid_id, img_dir, out_dir):
    """Calls openMVG for to perform the image listing
    Generates sfm_data.json file"""

    # Get the width of the frames by searching into dictionary of information
    width = get_dic_info(vid_id=vid_id)['width']

    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(img_dir, out_dir, width)

    os.system(command=cmd)


def openmvg_features(path_sfm, path_features):
    """Calls openMVG to do compute features
    Generates .desc and .feat in the dir given by path features for all the frames"""

    cmd = 'openMVG_main_ComputeFeatures -i {} -o {}'.format(path_sfm, path_features)
    os.system(cmd)


def openmvg_matches(path_sfm, path_matches):
    """Calls openMVG to do compute matches
    Generates various files: .bin , putative_matches ... """

    cmd = 'openMVG_main_ComputeMatches -i {} -o {}'.format(path_sfm, path_matches)
    os.system(cmd)


def openmvg_incremental(path_sfm, path_matches, path_incr):
    """Calles openMVG for the incremental
    Generates 3D models: .ply files"""

    cmd = "openMVG_main_IncrementalSfM -i {} -m {} -o {} ".format(path_sfm,
                                                                  path_matches,
                                                                  path_incr)
    os.system(cmd)


def openmvg_bin_to_json(path_data_bin, path_data_json):
    """Call openMVG to convert to convert the binary file to json"""

    cmd = "openMVG_main_ConvertSfM_DataFormat -i {} -o {}".format(path_data_bin, path_data_json)
    os.system(cmd)


def get_frms_pths(path_data_json, old_pth_frms, new_pth_frms):
    """Reads the json files generated by the incremental step and returns
    a tuple with the old and paths for the frames used. """

    # Load json data in a dic
    with open(path_data_json) as f:
        dic_incr = json.load(f)

    list_frames = list()
    # Loop over the elements at extrinsic node:
    for i in range(len(dic_incr['extrinsics'])):

        list_frames.append(dic_incr['views']
                           [dic_incr['extrinsics'][i]['key']]
                            ['value']
                             ['ptr_wrapper']
                              ['data']
                               ['filename'])

    # Generate list of tuples with the old and new paths
    list_tuple_paths = [(os.path.join(old_pth_frms, el),
                         os.path.join(new_pth_frms, el)) for el in list_frames]

    return list_tuple_paths


def move_frames(pair_paths):
    """Function used to move the frames after incremental step:
    takes a list of tuple as argument where the first entry of a tuple is
    the old path and the second entry is the new one """
    for pair in pair_paths:
        os.rename(pair[0], pair[1])


#


def sfm_it(vid_id, iter_number, path_frames, path_openmvg):
    """Performs one iteration of the procedure"""

    # Create iter dir
    path_out_dir = os.path.join(path_openmvg, 'iter_{}'.format(iter_number))
    make_dir(path_out_dir)

    # Listing #TODO change the way width is retrieved
    openmvg_list(vid_id=vid_id, img_dir=path_frames, out_dir=path_out_dir)

    # Computing features
    path_sfm = os.path.join(path_out_dir, 'sfm_data.json')
    path_features = os.path.join(path_out_dir, 'out_features')
    make_dir(path_features)

    openmvg_features(path_sfm=path_sfm, path_features=path_features)

    # Matching
    openmvg_matches(path_sfm=path_sfm, path_matches=path_features)

    # Incremental
    path_incr = os.path.join(path_out_dir, 'out_incremental')
    make_dir(path_incr)

    openmvg_incremental(path_sfm=path_sfm, path_matches=path_features, path_incr=path_incr)

    # Convert bin file to json
    path_data_bin = os.path.join(path_incr, 'sfm_data.bin')
    path_data_json = os.path.join(path_incr, 'sfm_data.json')

    openmvg_bin_to_json(path_data_bin=path_data_bin, path_data_json=path_data_json)

    # Generates the paths
    new_pth_frms = os.path.join(path_out_dir, 'frames')
    make_dir(new_pth_frms)
    list_tuple_path = get_frms_pths(path_data_json=path_data_json,
                                    old_pth_frms=path_frames,
                                    new_pth_frms=new_pth_frms)

    # Move frames that are used in 3D model
    move_frames(list_tuple_path)


def sfm_loop(vid_id):
    """ Performs the sfm loop"""
    path_vid_dir = pth_vid_dir(vid_id)
    path_frames = os.path.join(path_vid_dir,'frames')
    remove_ds_store(path_frames)
    path_openmvg = os.path.join(path_vid_dir, 'out_openMVG')
    make_dir(path_openmvg)

    remove_ds_store(path_frames)
    nbr_frms = len(os.listdir(path_frames))
    nbr_frms_temp = nbr_frms
    iter_nbr = 0

    while nbr_frms_temp/nbr_frms > 0.1:  #Todo change this condition
        print('Iteration {}'.format(iter_nbr))
        nbr_frms = len(os.listdir(path_frames))
        print('{:.2f}% of frames in main directory \n'.format(nbr_frms_temp/nbr_frms))
        sfm_it(vid_id=vid_id,
               iter_number=iter_nbr,
               path_frames=path_frames,
               path_openmvg=path_openmvg)
        iter_nbr += 1


































