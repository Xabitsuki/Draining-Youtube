from functions import *

def capture(url):
    ''''Functions that creates the vid directory, download the video
    and extract the frames.'''

    # Create vid dir and download
    yt_dl(url=url)
    v_id = url_to_id(url=url)

    # Extract frames
    frame_xtrct(v_id=v_id, use_sample=off)
    return v_id

def iter0(v_id):
    """Function used to make the first iteration of processing loop"""

    # Make iter0 dir
    path_dir = pth_vid_dir(v_id)
    path_iter0 = os.path.join(path_dir, 'iter0')
    make_dir(path_iter0)

    frm_dir = os.path.join(path_dir, 'frames')

    openmvg_list(v_id=v_id, frm_dir=frm_dir, out_dir=path_iter0)

    path_feat = os.path.join(path_iter0, 'features')
    make_dir(path_feat)

    sfm = 'sfm_data.json'
    path_sfm = os.path.join(path_iter0, sfm)

    openmvg_features(path_sfm=path_sfm, path_features=path_feat)
    openmvg_matches(path_sfm=path_sfm, path_matches=path_feat)
