import sys
sys.path.insert(0, '/home/dhacker/Draining-Youtube')

import os
from multiprocessing import cpu_count

from functions import remove
from master_functions import drain_one
from time import time

URL = 'https://www.youtube.com/watch?v=z5NQG3Lx5Kk'
DL_FORMAT = '248'
RATE = 2

CPU_NUMBER = int(cpu_count())



if __name__ == '__main__':
    t0 = time()

    path_vid = drain_one(url=URL,
                         playlist= 'test_drain_plyst',
                         dl_format=DL_FORMAT,
                         rate=RATE,
                         cpu_number=CPU_NUMBER)

    f = open(os.path.join(path_vid, 'reproduce_info'), mode='w+')
    f.write('URL: {}\n'.format(URL))
    f.write('DL_FORMAT: {}\n'.format(DL_FORMAT))
    f.write('RATE: {}\n'.format(RATE))
    f.close()

    print('time of execution: {}'.format(time()-t0))
