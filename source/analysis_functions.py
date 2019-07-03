from functions import *
from master_functions import *

import numpy as np
import pandas as pd


# Name of the columns
COLUMNS = ['Playlist',   #0
           'Youtube ID',   #1
           'Format',   #2
           'Duration',   #3
           'Extract Rate',   #4
           'Frames Total',   #5
           'Number of sets', #6
           'Set Number',   #7
           'Frames in Set', #8
           'Number of Vertices',#9
           'Average Distance', #10
           'Std Distance',  #11
           'Jumps in Trajectory',#12
           'Average Angle'] #13


def get_dl_rate(video,plylst):
    """Returns the rate at which the frames where
       extracted by reading the reproduce_info file.
       Returns the rate."""
    target = 'RATE: '
    rep_info = os.path.join(pth_vid(video,plylst), 'reproduce_info')
    pipe = open(rep_info, 'r')
    string_file = pipe.read()
    target = [el for el in string_file.split('\n') if el.startswith(target)][0]\
                .split(target)[1]
    return float(target)


def get_nbr_vertices(path_sfm):
    """ Read sf_data_file and get number of vertices.
        Return: nbr of vertices."""
    pipe = open(path_sfm, 'r')
    sfm_data = pipe.read()
    target = 'element vertex '
    n: int = int([el for el in sfm_data.split('\n') if el.startswith(target)][0].split(target)[1])
    return n


def get_vectors(path_incr):
    """Convert sfm_data.bin to sfm_data.json.
       Read the json file and return matrix containing
       all the vectors of the frames used in the incremental reconstruction.
       Return n by 3 matrix containing vectors."""

    sfm_bin = os.path.join(path_incr, 'sfm_data.bin')
    sfm_json = openmvg_convert_sfm_data_format(sfm_bin)
    # read json generated file
    with open(sfm_json) as json_data:
        dic = json.load(json_data)
    # get vetcors
    vec_list = list()
    for frm in dic['extrinsics']:
        vec_list.append(frm['value']['center'])
    vec_mat = np.asarray(vec_list)
    return vec_mat


def compute_distance_stats(vec_mat, threshold=2):
    """ Get mean of distances of the successif vectors used in the reconstruction.
        return mean an variance of the distances.
        A jump in a trajectory is counted when the distance between two
        consecutive vectors is greater than mean(distances) + threshold*std"""
    # Compute distances
    distances = []
    for i in range(vec_mat.shape[1] - 1):
        distances.append(np.linalg.norm(vec_mat[i + 1] - vec_mat[i]))

    distances = np.asarray(distances)
    mean = np.mean(distances)
    std = np.std(distances)

    # Count jumps
    nbr_jumps = 0
    for dist in distances:
        if dist >= mean + threshold * std:
            nbr_jumps += 1

    return (mean, std, nbr_jumps)


def compute_angle_stats(vec_mat, unit='deg'):
    """ Get mean of angles the successif vectors used in the reconstruction.
        return mean an variance of the angles.
        """
    angles = []
    for i in range(vec_mat.shape[1] - 1):
        aux = 0
        dot_prod = np.dot(vec_mat[i] / np.linalg.norm(vec_mat[i]),
                          vec_mat[i + 1] / np.linalg.norm(vec_mat[i + 1]))
        if dot_prod < 0:
            aux = np.pi
        angles.append(np.arccos(dot_prod) + aux)

    angles = np.asarray(angles)
    if unit == 'deg':
        angles *= 180 / np.pi
    mean = np.mean(angles)
    std = np.std(angles)

    return (mean, std)


def get_info_video_aux(v_id, plylst):
    """Get info of video and append it to the list.
       Output: [v_id, format, nbr frames, rate]"""
    data_list = list()

    data_list.append(plylst)  # 0

    data_list.append(v_id)  # 1

    # Info from Youtube
    info_dic = get_dic_info(v_id, plylst)
    width = info_dic['width']
    height = info_dic['height']
    data_list.append(np.asarray((width, height)))  # 2

    duration = info_dic['duration']
    data_list.append(duration)  # 3

    # Rate of frame extraction
    rate = get_dl_rate(v_id, plylst)
    data_list.append(rate)  # 4

    # Number of frames
    data_list.append(rate * duration)  # 5

    # Number of sets
    nbr_sets = len(os.listdir(pth_sets(v_id, plylst)))
    data_list.append(nbr_sets)  # 6
    return data_list


def get_info_sets(data_list):
    """Append to a data_list the information
       of the sets present in the video that
       the generate the data_list.
       Returns list of information lists."""

    sets = pth_sets(data_list[1], data_list[0])
    nbr_sets = data_list[6]
    rows = []

    for i in range(nbr_sets):
        cur = data_list.copy()
        # Set number
        cur.append(i)  # 7

        pth_set = os.path.join(sets, 'set_{}'.format(i))
        frames = os.path.join(pth_set, 'frames')
        # Number of frames in set
        cur.append(len(os.listdir(frames)))  # 8

        # Check sfm_data_color.ply file
        path_fail = os.path.join(pth_set, 'incremental_fail')
        path_incr = os.path.join(pth_set, 'incremental')
        path_sfm = os.path.join(path_incr, 'sfm_data_color.ply')

        fail = os.path.isdir(path_fail)
        incr = os.path.isdir(path_incr)
        sfm_py = os.path.isfile(path_sfm)

        if incr and sfm_py and not fail:
            # append number of vertices
            cur.append(get_nbr_vertices(path_sfm))  # 9

            # Stats
            vec_mat = get_vectors(path_incr)
            # Check if reconstruction is not empty
            if vec_mat.shape[0] == 0:
                cur.append(np.nan)  # 10
                cur.append(np.nan)  # 11
                cur.append(np.nan)  # 12
                cur.append(np.nan)  # 13

            else:
                distances = compute_distance_stats(vec_mat)
                cur.append(distances[0])  # 10
                cur.append(distances[1])  # 11
                cur.append(distances[2])  # 12
                cur.append(compute_angle_stats(vec_mat)[0])  # 13
        else:
            cur.append(np.nan)  # 9
            cur.append(np.nan)  # 10
            cur.append(np.nan)  # 11
            cur.append(np.nan)  # 12
            cur.append(np.nan)  # 13

        rows.append(cur)

    return rows


def get_rows_video(v_id, plylst):
    """Functions to generate lists of information on the
       sets extracted from a video.
       The lists are used to generate dataframes of the video.
       Return a list of lists."""
    rows_vid = get_info_sets(get_info_video_aux(v_id, plylst)).copy()
    return rows_vid


def get_rows_playlist(plylst):
    """Returns a list containing all the lists of information
       of all the sets generated among all the video of the playlist. """
    playlist = pth_plylst(name=plylst)

    remove_ds_store(plylst)
    rows = []
    for v_id in os.listdir(playlist):
        rows.extend(get_rows_video(v_id, plylst))

    return rows


def get_df_playlist(playlist):
    """Function to generate a dataframe of the
       inspected playslist.
       Returns datafame of the playlist."""

    global COLUMNS
    return pd.DataFrame(data=get_rows_playlist(playlist), columns=COLUMNS)
