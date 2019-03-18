import os
import time

from class_timer import Timer

def path_to_vid_dir(vid_id):
    '''returns full path to video dir assuming call from main folder'''
    return os.path.join(os.getcwd(), 'videos', vid_id)


def path_to_vid_file(vid_id, format):
    '''returns full path to video file assuming call from main folder'''

    # search for file in path
    path = path_to_vid_dir(vid_id=vid_id)

    # Look for file matching the format
    vid_file = [el for el in os.listdir(path) if el.endswith(format)][0] #TODO: should throw error if no file

    return os.path.join(path_to_vid_dir(vid_id), vid_file)


def vid_xtrct(vid_id, format,start=0, stop=30):
    '''creates a copy of the video that begins at start (in seconds) parameter and ends at ends at stop (in seconds)
    parameter  '''

    start = time.strftime("%H:%M:%S", time.gmtime(start))
    stop = time.strftime("%H:%M:%S", time.gmtime(stop))

    split = path_to_vid_file(vid_id=vid_id, format=format).split(sep='.', maxsplit=1)

    path_to_trim_file = '{}-{}-{}.{}'.format(split[0], start, stop, split[1])

    cmd_str = 'avconv -i {} -s {} -t {} -codec copy {}'.format(path_to_vid_file(vid_id=vid_id, format=format),
                                                               start,
                                                               stop,
                                                               path_to_trim_file)
    os.system(cmd_str)


def frame_xtrct(vid_id, format, imgs_per_sec=2):

    """ Creates a directory that contains the frames the extracted frames and extracts the frames calling avconv"""

    path_vid_dir = path_to_vid_dir(vid_id)
    path_frames_dir = os.path.join(path_vid_dir, 'frames')

    # Create "frame" directory:
    if not os.path.isdir(path_frames_dir):
        os.mkdir(path_frames_dir)

    # Extract frames using specified rate and format
    path_file = path_to_vid_file(vid_id=vid_id, format=format)

    cmd_str = 'avconv -i {} -r {} -f image2 {}/frame%04d.png'.format(path_file,
                                                                     imgs_per_sec,
                                                                     path_frames_dir)
    os.system(cmd_str)


if __name__ == '__main__':

    vid_id = 'R3AKlscrjmQ'
    start = 10
    stop = 40


    def image_list(yt_id, image_directory='frames', out_directory='out_openMVG'):
        # Get the width of the frames by searching into dictionary of information

        cmd = "openMVG_main_SfMInit_ImageListing -i {} -o {} -f {}".format(image)


    timer = Timer()



    timer.start()
    print('Vid extract')
    vid_xtrct(vid_id=vid_id, format='.webm', start=start, stop=stop)
    timer.stop()

    timer.start()
    print('frame extract')
    frame_xtrct(vid_id=vid_id, format='-00:00:10-00:00:40.webm') # TODO coder fonction pour le format
    timer.stop()
