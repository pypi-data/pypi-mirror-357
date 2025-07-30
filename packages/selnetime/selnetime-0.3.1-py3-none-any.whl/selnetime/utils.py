import time

class Timer(object):
    def __init__(self, name=None, filename=None, verbosity=3):
        self.name = name
        self.filename = filename
        self.verbosity = verbosity

    def __enter__(self):
        self.tstart = time.time()
        if self.name:
            message = '[%s] starts' % self.name
            if self.verbosity >= 2:
                print(message)

    def __exit__(self, type, value, traceback):
        message = 'Elapsed: %.2f seconds' % (time.time() - self.tstart)
        if self.name:
            message = '[%s] ' % self.name + message
        if self.verbosity >= 2:
            print(message)
        if self.filename:
            with open(self.filename,'a') as file:
                if self.verbosity >= 2:
                    print(str(datetime.datetime.now())+": ",message,file=file)
