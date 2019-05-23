import os
from multiprocessing import  Process

from functions import *



def get_plylst_id(path_vid):

    split = path_vid.split(sep=pth_vids())[1].split('/')
    if len(split) == 3:

        plylst = split[1]
        id_ = split[2]

        return id_, plylst

    elif len(split) == 2:

        id_ = split[1]
        return id_, ''


def make_sets(v_id, plylst=''):
    """Used after the iter_0 function ran to separate the frames into sets.
    Return the path the to the sets folder"""

    triangles = split_triangles(bin_matches_to_adja_mat(path_mtchs=pth_iter0_mtchs(v_id, plylst),
                                                        path_frames=pth_frms(v_id, plylst)))

    return move_triangles(triangles=triangles,
                          path_vid=pth_vid(v_id, plylst),
                          path_frames=pth_frms(v_id, plylst),
                          path_feats=pth_iter0_feats(v_id, plylst))


def iter0(path_vid, rate, frame_force=False, feature_force=False, match_force=False, sample=False):
    """Function used to make the first iteration of processing loop.
    Return: path_sets, width"""
    v_id, plylst = get_plylst_id(path_vid)

    # Extract frames
    if frame_force or not os.path.isdir(pth_frms(v_id, plylst)):
        xtrct_frame(v_id, plylst, sample, rate)

    # Make iter0 dir
    pth_it0 = pth_iter0(v_id, plylst)
    make_dir(pth_it0)

    # Listing
    path_frms = pth_frms(v_id, plylst)
    width = get_dic_info(path_vid)['width']
    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(path_frms, pth_it0, width)
    os.system(command=cmd)

    # Compute features
    path_feat = pth_iter0_feats(v_id, plylst)
    if feature_force or not os.path.isdir(path_feat):
        if os.path.isfile(path_feat):
            os.system('rm -rf path_feat')
        make_dir(path_feat)

        path_sfm = os.path.join(pth_it0, 'sfm_data.json')
        cmd = 'openMVG_main_ComputeFeatures -i {} -o {}'.format(path_sfm, path_feat)
        os.system(cmd)

    # Compute  matches
    if match_force or not os.path.isfile(pth_iter0_mtchs(v_id, plylst)):

        path_sfm = os.path.join(pth_it0, 'sfm_data.json')
        cmd = 'openMVG_main_ComputeMatches -i {} -o {}'.format(path_sfm, path_feat)
        os.system(cmd)

    # Make sets
    path_sets = pth_sets(v_id, plylst)
    if match_force or not os.path.isdir(path_sets):
        path_sets = make_sets(v_id, plylst)

    remove_ds_store(path_sets)
    return path_sets, width


def sfm_pipe(pth_set, width):
    """Function that performs the sfm pipeline given the path to
    a set as generated by make_sets."""

    frames = os.path.join(pth_set, 'frames')
    features = os.path.join(pth_set, 'features')

    openmvg_list(width=width, pth_frms=frames, pth_out=pth_set)

    path_sfm = pth_sfm(pth_set)

    openmvg_features(pth_sfm=path_sfm, pth_features=features)

    openmvg_matches(pth_sfm=path_sfm, pth_matches=features)

    path_incr = os.path.join(pth_set, 'incremental')
    make_dir(path_incr)

    openmvg_incremental(pth_sfm=path_sfm, pth_matches=features, pth_incr=path_incr)

    openmvg_colors(pth_incr=path_incr)


def master_iter0(args):
    """Performs iter0() and launch sfm_pipe processes with
    the generated sets."""

    path_set_dir, width = iter0(*args)
    pth_sets = [os.path.join(path_set_dir, el) for el in os.listdir(path_set_dir)]
    # start new process
    for pth_set in pth_sets:
        args = (pth_set, width)
        Process(target=sfm_pipe, args=args).start()

def launching(rate, f_frms, f_ftrs, f_mtchs, sample, plylsts=[], vids=[]):
    for plylst in plylsts:
        for v_id in os.listdir(pth_plylst(plylst)):
            args = (pth_vid(v_id, plylst), rate, f_frms, f_ftrs, f_mtchs, sample)
            Process(target=master_iter0, args=args).start()

    for v_id in vids:
        args = (pth_vid(v_id), rate, f_frms, f_ftrs, f_mtchs, sample)
        Process(target=master_iter0, args=(args,)).start()

def drain(rate, f_frms, f_ftrs, f_mtchs, sample, plylsts=[], vids=[]):
    print('Start Draining')
    execution = Process(target=launching, args=(rate, f_frms, f_ftrs, f_mtchs, sample, plylsts, vids))
    execution.start()
    execution.join()
    print('Finish Draining')

#####################################################################################################

def iter0(path_vid, rate, frame_force=False, feature_force=False, match_force=False, sample=False):
    """Function used to make the first iteration of processing loop.
    Return: path_sets, width"""
    v_id, plylst = get_plylst_id(path_vid)

    # Extract frames
    if frame_force or not os.path.isdir(pth_frms(v_id, plylst)):
        xtrct_frame(v_id, plylst, sample, rate)

    # Make iter0 dir
    pth_it0 = pth_iter0(v_id, plylst)
    make_dir(pth_it0)

    # Listing
    path_frms = pth_frms(v_id, plylst)
    width = get_dic_info(path_vid)['width']
    cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(path_frms, pth_it0, width)
    os.system(command=cmd)

    # Compute features
    path_feat = pth_iter0_feats(v_id, plylst)
    if feature_force or not os.path.isdir(path_feat):
        if os.path.isfile(path_feat):
            os.system('rm -rf path_feat')
        make_dir(path_feat)

        path_sfm = os.path.join(pth_it0, 'sfm_data.json')
        cmd = 'openMVG_main_ComputeFeatures -i {} -o {}'.format(path_sfm, path_feat)
        os.system(cmd)

    # Compute  matches
    if match_force or not os.path.isfile(pth_iter0_mtchs(v_id, plylst)):

        path_sfm = os.path.join(pth_it0, 'sfm_data.json')
        cmd = 'openMVG_main_ComputeMatches -i {} -o {}'.format(path_sfm, path_feat)
        os.system(cmd)

def iter0_seq(args_iter0, shared_list):
    """Calls iter= and append the return to the shared_list"""
    paths_sets, width = iter0(*args_iter0)
    for pth in paths_sets:
        shared_list.append((pth, width))


def launching_seq_aux(target, args_l):
    """ Function used to launch Processes in parallel"""
    for args in args_l:
        Process(target=target, args=args).start()


def launching_seq(vids_list, rates=1, cpu_nbr=8, f_frms=True, f_ftrs=True, f_mtchs=True, sample=False):
    """Function that spawns at maximum a number of processes equal to the parameter cpu_nbr."""
    manager = Manager()
    shared_list = manager.list()

    # Repeat until all vids have been processed

    target = iter0_seq
    while not vids_list.empty():

        args_l=[]
        if len(vids_list) >= cpu_nbr:
            for i in range(cpu_nbr):
                args_iter0 = (pth_vid(v_id=vids_list.pop), rates[-i-1], f_frms, f_ftrs, f_mtchs, sample)
                args_l.append((args_iter0, shared_list))

        else: # less videos than cpu_numbers
            for i in range(len(vids_list)):
                args_l.append((pth_vid(v_id=vids_list.pop), rates[-i - 1], f_frms, f_ftrs, f_mtchs, sample))

        control_launch = Process(target=launching_seq_aux, args=(target, args_l))
        control_launch.start()
        control_launch.join()

    # Finish iter0 part
    target = sfm_pipe
    while not sfm_pipe_list.empty():

        args_l = []
        if len(shared_list) >= cpu_nbr:
            for i in range(cpu_nbr):
                args_l.append(shared_list.pop())

        else: # less sfm_pipe remaining than cpu_number

            for i in range(len(shared_list)):
                args_l.append(shared_list.pop())

        control_launch = Process(target=launching_seq_aux, args=(target, args_l))
        control_launch.start()
        control_launch.join()