import sys
sys.path.insert(0, '../source/')
import os
from time import time
from multiprocessing import cpu_count
from master_functions import drain_one



# Link of the videos to be downloaded and processed
# https://www.youtube.com/watch?v=LnyKeqdzQao is test
# video of a drain flight over the city of Lausanne.
URL = 'https://www.youtube.com/watch?v=LnyKeqdzQao'


# Name of the playlist folder in videos/ containing the video directories
PLAYLIST = 'test_video'

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
    path_vid = drain_one(url=URL,
                         playlist=PLAYLIST,
                         dl_format=DL_FORMAT,
                         rate=RATE,
                         parallel_tasks=TASKS_IN_PAR,
                         sample=SAMPLE,
                         video_mode=VIDEO_MODE)

    f = open(os.path.join(path_vid, 'reproduce_info'),
             mode='w+')
    f.write('URL: {}\n'.format(URL))
    f.write('DL_FORMAT: {}\n'.format(DL_FORMAT))
    f.write('RATE: {}\n'.format(RATE))
    f.write('VIDEO_MODE: {}\n'.format(VIDEO_MODE))
    f.close()
    print('Execution finished in {}s'.format(time() - t0))
