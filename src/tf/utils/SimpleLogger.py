
class SimpleLogger(object):
    def __init__(self, path='.'):
        self.logger = open("{:s}/debug_log.txt".format(path), "w")

    def log(self, *args):
        to_write = " ".join([str(a) for a in args])
        self.logger.write(to_write + '\n')
        self.logger.flush()
