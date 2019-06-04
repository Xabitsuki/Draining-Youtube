from __future__ import unicode_literals
import youtube_dl
import os
import shutil
import time
import json
import numpy as np

PROJ_NAME = 'Draining-Youtube'

#######################################  Unixs

def remove(path):
    """Remove file/dir"""

    if os.path.isfile(path):
        os.remove(path)
        return

    if os.path.isdir(path):
        shutil.rmtree(path)


def remove_ds_store(path_folder):
    """Remove .DS_Store from in folder"""

    path_ds_store = '{}/.DS_Store'.format(path_folder)

    if os.path.isfile(path_ds_store):
        os.remove(path_ds_store)


def make_dir(pth_dir):
    if not os.path.isdir(pth_dir):
        os.mkdir(pth_dir)


#######################################  Path functions


def pth_prj(prj_name=PROJ_NAME):

    cur_dir = os.getcwd()
    split = cur_dir.split(prj_name)
    return os.path.join(split[0], prj_name)


def pth_vids():
    """Return path to videos/ folder"""

    pth = os.path.join(pth_prj(), 'videos')
    remove_ds_store(pth)
    return pth


def pth_plylst(name):
    """Return path to playlist folder in videos folder"""

    pth = os.path.join(pth_vids(), name)
    remove_ds_store(pth)
    return(pth)


def pth_vid(v_id, plylst=''):
    """Returns full path to video dir assuming call from main folder"""
    if not plylst:
        pth = os.path.join(pth_vids(), v_id)
        remove_ds_store(pth)
        return (pth)

    else:
        pth = os.path.join(pth_plylst(name=plylst), v_id)
        remove_ds_store(pth)
        return (pth)


def pth_data(v_id, plylst):
    """Returns full path to video file assuming call from main folder"""
    path_vid = pth_vid(v_id=v_id, plylst=plylst)
    path_data = os.path.join(path_vid, 'data')
    remove_ds_store(path_data)

    # Look for file that is not .info.json
    vid_file = [el for el in os.listdir(path_data) if not el.endswith('.info.json')][0]
    return os.path.join(path_data, vid_file)


def pth_frms(v_id, plylst=''):
    return os.path.join(pth_vid(v_id, plylst), 'frames')


def pth_iter0(v_id, plylst=''):
    return os.path.join(pth_vid(v_id, plylst), 'iter0')


def pth_iter0_feats(v_id, plylst=''):
    return os.path.join(pth_vid(v_id, plylst), 'iter0', 'features')


def pth_iter0_mtchs(v_id, plylst=''):
    return os.path.join(pth_iter0_feats(v_id, plylst), 'matches.f.txt')


def pth_sets(v_id, plylst):
    return os.path.join(pth_vid(v_id, plylst), 'sets')


def pth_sfm(pth):
    """returns path to sfm (first found) file if found at location
       given by pth or None if no file found"""

    list_sfm = [el for el in os.listdir(pth) if el.startswith('sfm_')]

    if not len(list_sfm) == 0:
        return os.path.join(pth, list_sfm [0])
    else:
        return None


def get_plylst_id(path_vid):
    """Get v_id and plylst ba parsinh vid path.
    Returns v_id, plylst"""

    split = path_vid.split(sep=pth_vids())[1].split('/')
    if len(split) == 3:

        plylst = split[1]
        v_id = split[2]

        return v_id, plylst

    elif len(split) == 2:

        v_id = split[1]
        return v_id, ''

#######################################  Youtube-dl


def url_to_id(url):
    """Take an url and return the youtube id that it contains"""

    return url.split(sep='watch?v=')[1].split('=')[0]


def gen_items(n_items):
    """"Function used in yt_dl to generate the string of indices  corresponding to the desired
        number of items to be downloaded."""

    items = '1'
    for ii in range(2,n_items):
        items = '{},{}'.format(items, ii)
    items = '{},{}'.format(items, n_items)
    return items


def yt_dl(url, playlist='', format=None, n_items=1):
    """Call youtube-dl to download a video providing the url.
       By default provides an output template to store all the videos in
       a single directory, name them by id and extension and
       write information in json file"""
    opts = dict()
    if playlist:
        opts['outtmpl'] = 'videos/{}/%(id)s/data/%(id)s_%(resolution)s.%(ext)s'.format(playlist)
        opts['writeinfojson'] = True
        opts['playlist_items'] = gen_items(n_items=n_items)

    else:
        opts['outtmpl'] = 'videos/%(id)s/data/%(id)s_%(resolution)s.%(ext)s'
        opts['writeinfojson'] = True
        opts['noplaylist'] = 'no'

    if format:
        opts['format'] = format

    with youtube_dl.YoutubeDL(opts) as ydl:
        ydl.download([url])

    return url_to_id(url), playlist


def get_dic_info(v_id, plylst):
    """Load the info dictionnary created by youtube-dl when the video was downloaded."""

    path_data = os.path.join(pth_vid(v_id=v_id, plylst=plylst), 'data')

    list_ = [el for el in os.listdir(path_data) if el.endswith('.info.json')]
    path_info = os.path.join(path_data, list_[0])

    with open(path_info) as f:
        dic_info = json.load(f)

    return dic_info


#######################################  ffmpeg Wrapping


def xtrct_frame(v_id, plylst='', sample=False, rate=2, start=0, stop=30):
    """ Creates a directory that contains the frames the extracted
        frames and extracts the frames calling avconv"""

    path_data = pth_data(v_id=v_id, plylst=plylst)

    # Create "frame" directory:
    path_frames = pth_frms(v_id=v_id, plylst=plylst)
    make_dir(path_frames)

    if sample:
        cmd = 'ffmpeg -i {} -ss {} -t {} -r {} -f image2 {}/frame%04d.png'.format(path_data,
                                                                                  start,
                                                                                  stop,
                                                                                  rate,
                                                                                  path_frames)

    else:
        cmd = 'ffmpeg -i {} -r {} -f image2 {}/frame%04d.png'.format(path_data,
                                                                     rate,
                                                                     path_frames)
    os.system(cmd)


def xtrct_vid(path_data, path_new_data, start=0, stop=30, remove=False):
    """creates a copy of the video that begins at start (in seconds) parameter and
       ends at ends at stop (in seconds) parameter"""

    cmd_str = 'ffmpeg -i {} -ss {} -t {} -codec copy {}'.format(path_data,
                                                                start,
                                                                stop,
                                                                path_new_data)
    os.system(cmd_str)


#######################################  OpenMVG wrapping


def openmvg_list(width, pth_frms, pth_out):
    """Calls openMVG for to perform the image listing
       Generates sfm_data.json file"""

    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(pth_frms, pth_out, width)
    os.system(cmd)


def openmvg_features(pth_sfm, pth_features, force=False):
    """Calls openMVG to do compute features
       Generates .desc and .feat in the dir given by path features for all the frames"""

    cmd = 'openMVG_main_ComputeFeatures -i {} -o {}'.format(pth_sfm, pth_features)
    if force: cmd = cmd + " -f 1"
    os.system(cmd)


def openmvg_matches(pth_sfm, pth_matches, video_mode=5, force=False):
    """Calls openMVG to do compute matches
       Generates various files: .bin , putative_matches ... """

    cmd = "openMVG_main_ComputeMatches -i {} -o {} -v {}".format(pth_sfm, pth_matches, video_mode)
    if force:
        cmd = cmd + " -f 1"
    os.system(cmd)


def openmvg_incremental(pth_sfm, pth_matches, pth_incr):
    """Calles openMVG for the incremental
       Auto is a flag to be used in sfm to automatize the execution.
       Generates 3D models: .ply files"""

    cmd = "openMVG_main_IncrementalSfM2 -i {} -m {} -o {} ".format(pth_sfm, pth_matches, pth_incr)

    os.system(cmd)


def openmvg_colors(pth_incr):
    """Functions to call openMVG_main_ComputeSfM_DataColor to add
       the colors on the points of the 3D model.
       If incremental step failed (no sfm_data_color.ply file),
       renames the folder incremental_fail"""

    path_sfm = os.path.join(pth_incr,'sfm_data.bin') # Should not be hardcoded
    if os.path.isfile(path_sfm):
        path_ply = os.path.join(pth_incr, 'sfm_data_color.ply')
        cmd = 'openMVG_main_ComputeSfM_DataColor -i {} -o {}'.format(path_sfm, path_ply)
        os.system(cmd)
    else:
        os.renames(old=pth_incr, new='{}_fail'.format(pth_incr))


def openmvg_convert_sfm_data_format(pth_in):
    """Call openMVG to convert sfm_data.XXX
       to sfm_data.json.
       Return path to generated file."""

    pth_out = pth_in.split('.')[0] + '.json'

    if not os.path.isfile(pth_out):
        cmd = 'openMVG_main_ConvertSfM_DataFormat -i {} -o {}'.format(pth_in, pth_out)
        os.system(cmd)
    return pth_out


#######################################  Extract Triangles


def line_to_tuple(line):
    """Used to read matches.f.txt file in extract_matches"""

    return (int(line.split(sep=' ', maxsplit=1)[0]),
            int(line.split(sep=' ', maxsplit=1)[1]))


def extract_matches(path_mtchs):
    """function to read the matches.f.txt file to extract the matches.
       Return: match_list"""

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


def bin_matches_to_adja_mat(path_mtchs, path_frames):
    """Returns adjacency matrix provided the path to the matches
       and the path to the frames (used in iter0)."""

    return make_adj_mat(extract_matches(path_mtchs), path_frames)


def split_triangles(adj_mat, tol=30):
    """Provides a list containing tuples that describe
       triangles of images that match : the triangle are composed of the points
       (i_min, i_min+1), (i_min, i_max), (i_max-1, i_max) in the adjacency matrix."""

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

                while j != length-1 and abs(non_zer[j+1] - non_zer[j]) < tol:
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


def move_triangles(triangles, path_vid, path_frames, path_feats):
    """Function used to move the frames and their .desc and .feat files
       from main folder to sub-fub folders created.
       Generates: - sets/
                  - sets/set_i
                  - sets/set_i/frames
                  - sets/set_i/features"""
    s = 0
    path_sets = os.path.join(path_vid, 'sets')
    make_dir(path_sets)

    for t in triangles:

        path_new_folder = os.path.join(path_sets, 'set_{}'.format(s))
        make_dir(path_new_folder)

        path_frames_n = os.path.join(path_new_folder, 'frames')
        make_dir(path_frames_n)

        path_feats_n = os.path.join(path_new_folder, 'features')
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

    return path_sets
