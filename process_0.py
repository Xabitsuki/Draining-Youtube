from functions import *

url = 'https://www.youtube.com/watch?v=1Rq9b_bn6Bc'
vid_id = url_to_id(url)
vid_file = 'slice0.mp4'

# The frames in the frames dir come from the slice0.mp4 file

if __name__ == '__main__':

    # Iter 0
    iter0(vid_id=vid_id)

    path_dir = pth_vid_dir(vid_id=vid_id)
    path_iter0 = os.path.join(path_dir, 'iter0')
    path_sfm = os.path.join(path_iter0, 'sfm_data.json')
    path_feat = os.path.join(path_iter0, 'features')
    path_incr = os.path.join(path_dir, 'incremental')
    make_dir(path_incr)

    openmvg_incremental(path_sfm=path_sfm,
                        path_matches=path_feat,
                        path_incr=path_incr)
