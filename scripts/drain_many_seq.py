import sys
sys.path.insert(0, '../source/')
import os
from time import time
from multiprocessing import cpu_count
from functions import pth_vid, url_to_id
from master_functions import drain_many_seq



# Links of the videos to be downloaded and processed
URLS = ['https://www.youtube.com/watch?v=9LgeDcu-oho',
        'https://www.youtube.com/watch?v=LnyKeqdzQao']

# Name of the playlist folder in videos/ containing the video directories
PLAYLIST = 'multiple_downloads'

# Format for download
# 244          webm       854x480    	 480p
# 247          webm       1280x720       720p
# 248          webm       1920x1080      1080p
# 271          webm       2560x1440      1440p
# 313          webm       3840x2160      2160p
DL_FORMAT = '248'

# If True extract frames from to 00:00 to 05:00 (time in video)
SAMPLE = True

# Rate of frame extraction
RATE = 2

# Number of tasks executed in paralell
TASKS_IN_PAR = int(cpu_count()/2)

# Refers to the video mode parameter of openMVG compute matches
VIDEO_MODE = 30


if __name__ == '__main__':
    t0 = time()
    drain_many_seq(urls=URLS.copy(),
                   plylst=PLAYLIST,
                   dl_format=DL_FORMAT,
                   rate=RATE,
                   parallel_tasks=TASKS_IN_PAR,
                   sample=SAMPLE, frame_force=False,
                   feature_force=False,
                   match_force=False, video_mode=VIDEO_MODE)

    for url in URLS:
        f = open(os.path.join(pth_vid(url_to_id(url), PLAYLIST),
                              'reproduce_info'),
                 mode='w+')
        f.write('URL: {}\n'.format(url))
        f.write('DL_FORMAT: {}\n'.format(DL_FORMAT))
        f.write('RATE: {}\n'.format(RATE))
        f.write('VIDEO_MODE: {}\n'.format(VIDEO_MODE))
        f.close()
    print('Execution finished in {}s'.format(time()-t0))
