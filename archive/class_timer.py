import time


class Timer:

    def __init__(self):
        self.time = 0

    def start(self):
        self.time = time.time()

    def stop(self, print_flag=True):
        self.time = time.time() - self.time

        pretty_time = time.strftime("%H:%M:%S", time.gmtime(self.time))
        if print_flag : print('\nExecution time : {}\n'.format(pretty_time))
