from __future__ import unicode_literals
import youtube_dl
import os
import time
import json
import numpy as np


# Class


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


# Unix


def remove_ds_store(path):

    """Remove .DS_Store file"""
    path_ds_store = '{}/.DS_Store'.format(path)

    if os.path.isfile(path_ds_store):
        os.remove(path_ds_store)


def make_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


# Get paths

def pth_prj(prj_name='Draining-Youtube'):

    cur_dir = os.getcwd()
    split = cur_dir.split(prj_name)
    return os.path.join(split[0], prj_name)


def pth_vid_dir(vid_id):
    """2returns full path to video dir assuming call from main folder"""

    return os.path.join(pth_prj(), 'videos', vid_id)


def pth_vid_file(vid_id, vid_format):
    """returns full path to video file assuming call from main folder"""

    # search for file in path
    path = pth_vid_dir(vid_id=vid_id)

    # Look for file matching the format
    vid_file = [el for el in os.listdir(path) if el.endswith(vid_format)][0]  # TODO: should throw error if no file

    return os.path.join(pth_vid_dir(vid_id), vid_file)


# Youtube-dl

def url_to_id(url):

    return url.split(sep='watch?v=')[1]


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


# ffmpeg Wrapping

def vid_xtrct(vid_id, vid_file, new_vid_file, start=0, stop=30):
    """creates a copy of the video that begins at start (in seconds) parameter and
     ends at ends at stop (in seconds) parameter"""

    path_vid_dir = pth_vid_dir(vid_id=vid_id)
    path_vid_file = os.path.join(path_vid_dir, vid_file)
    path_new_vid = os.path.join(path_vid_dir, new_vid_file)

    cmd_str = 'ffmpeg -i {} -ss {} -t {} -codec copy {}'.format(path_vid_file,
                                                                start,
                                                                stop,
                                                                path_new_vid)
    os.system(cmd_str)


def frame_xtrct(vid_id, vid_file, rate=2):

    """ Creates a directory that contains the frames the extracted
    frames and extracts the frames calling avconv"""

    # Create "frame" directory:
    path_vid_dir = pth_vid_dir(vid_id)
    path_frames = os.path.join(path_vid_dir, 'frames')
    make_dir(path_frames)

    # Extract frames using specified rate and format
    path_vid = os.path.join(path_vid_dir, vid_file)

    cmd_str = 'ffmpeg -i {} -r {} -f image2 {}/frame%04d.png'.format(path_vid,
                                                                     rate,
                                                                     path_frames)
    os.system(cmd_str)


# OpenMVG wrapping


def openmvg_list(vid_id, frm_dir, out_dir):
    """Calls openMVG for to perform the image listing
    Generates sfm_data.json file"""

    # Get the width of the frames by searching into dictionary of information
    width = get_dic_info(vid_id=vid_id)['width']

    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(frm_dir, out_dir, width)

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


def openmvg_colors(path_incr):
    """Functions to call openMVG_main_ComputeSfM_DataColor to add
    the colors on the points of the 3D model"""

    path_sfm = os.path.join(path_incr, 'sfm_data.bin')
    path_ply = os.path.join(path_incr, 'sfm_data_color.ply')

    cmd = 'openMVG_main_ComputeSfM_DataColor -i {} -o {}'.format(path_sfm, path_ply)

    os.system(cmd)


def openmvg_bin_to_json(path_data_bin, path_data_json):
    """Call openMVG to convert to convert the binary file to json"""

    cmd = "openMVG_main_ConvertSfM_DataFormat -i {} -o {}".format(path_data_bin, path_data_json)
    os.system(cmd)


# Loop / Parallelize


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

    # Listing
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


# Iter 0

def iter0(vid_id):
    """Function used to make the first iteration of processing loop"""

    # Make iter0 dir
    path_dir = pth_vid_dir(vid_id)
    path_iter0 = os.path.join(path_dir, 'iter0')
    make_dir(path_iter0)

    frm_dir = os.path.join(path_dir, 'frames')

    openmvg_list(vid_id=vid_id, frm_dir=frm_dir, out_dir=path_iter0)

    path_feat = os.path.join(path_iter0, 'features')
    make_dir(path_feat)

    sfm = 'sfm_data.json'
    path_sfm = os.path.join(path_iter0, sfm)

    openmvg_features(path_sfm=path_sfm, path_features=path_feat)
    openmvg_matches(path_sfm=path_sfm, path_matches=path_feat)


# Extract Triangles


def line_to_tuple(line):
    return (int(line.split(sep=' ', maxsplit=1)[0]),
            int(line.split(sep=' ', maxsplit=1)[1]))


def extract_matches(path_mtchs):
    """function to read the matches.f.txt file to extract the matches"""

    # Open and read matches file
    f = open(path_mtchs, mode='r')
    string_file = f.read()

    # Convert to list of lines
    lines = string_file.split(sep='\n')

    nbr_lines = len(lines)
    match_list = list()
    reach_end = False
    i = 0

    while not reach_end:
        match_list.append(line_to_tuple(lines[i]))
        i = i + 2 + int(lines[i + 1])
        if i + 1 == nbr_lines: reach_end = True

    return match_list


def make_adj_mat(match_list, path_frames):
    """Function to recreate an adjacency matrix out of
    the match_list passed as argument."""

    # retrieve size of matrix
    remove_ds_store(path_frames)
    n = len(os.listdir(path_frames))

    # initialize matrix
    adj_mat = np.zeros((n, n))

    idx = np.asarray(match_list)

    # slice the matrix with correct idxs
    adj_mat[idx[:, 0], idx[:, 1]] = 1

    return adj_mat


def mtchs_bin_to_mat(path_mtchs, path_frames):

    return make_adj_mat(extract_matches(path_mtchs), path_frames)


def split_triangles(adj_mat, tol=30):
    """Provides the provides a list containing tuples that decribe
    triangles of images that match : the triangle are composed of the points
    (i_min, i_min+1), (i_min, i_max), (i_max-1, i_max) in the adjacency matrix """

    n = adj_mat.shape[0]
    triangles = list()
    i_min = 0
    i_max = 0

    for i in range(0, n):

        # Retrieve non zero value for current line
        non_zer = np.nonzero(adj_mat[i])[0]

        # check if at begining or triangle
        if non_zer.size > 0:

            # check if no far image is taken into account
            if abs(non_zer[-1] - non_zer[0]) >= tol:

                length = len(non_zer)
                j = 0

                while j != length and abs(non_zer[j+1] - non_zer[j]) < tol:
                    j += 1

            # no far image: take them all
            else:
                i_max = non_zer[-1]

        # empty triangle or at end of triangle
        else:
            if i == i_max:
                # Close triangle
                if i_min < i_max:
                    triangles.append((i_min, i_max))
                i_min = i_max = i_max + 1

    return triangles


def move_triangles(triangles, path_frames, path_vid, path_feats):
    """Functions used to move the frames and their .desc and .feat files
    from main folder to sub-fub folders created """
    s = 0
    for t in triangles:

        path_new_folder = os.path.join(path_vid, 'set_{}'.format(s))
        make_dir(path_new_folder)

        path_frames_n = os.path.join(path_new_folder, 'frames')
        make_dir(path_frames_n)

        path_feats_n = os.path.join(path_new_folder, 'out_features')
        make_dir(path_feats_n)

        for i in range(t[0], t[1] + 1):

            frame = 'frame{:0>4.0f}'.format(i + 1)
            frame_png = '{}.png'.format(frame)
            frame_desc = '{}.desc'.format(frame)
            frame_feat = '{}.feat'.format(frame)

            # move frames
            try:
                os.rename(os.path.join(path_frames, frame_png),
                          os.path.join(path_frames_n, frame_png))
            except FileNotFoundError:
                pass
            # move .desc and .feat
            try:
                os.rename(os.path.join(path_feats, frame_desc),
                          os.path.join(path_feats_n, frame_desc))
            except FileNotFoundError:
                pass
            try:
                os.rename(os.path.join(path_feats, frame_feat),
                          os.path.join(path_feats_n, frame_feat))
            except FileNotFoundError:
                pass
        s += 1

