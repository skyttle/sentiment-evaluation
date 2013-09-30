import threading
import logging

LOGGER = logging.getLogger('APICompare.Thr')


class Thr(threading.Thread):
    """The class for threads, subclassed from threading.Thread class
    """
    inputs = {}
    outputs = {}
    lock = threading.Lock()

    def __init__(self, analyzer, args=[]):
        threading.Thread.__init__(self)
        self.id = analyzer.name
        self.func = analyzer.analyse
        self.args = args

    def run(self):
        Thr.inputs[self.id] = self.args
        try:
            output = self.func(*self.args)
        except Exception, exc:
            LOGGER.exception(exc)
            output = (None, exc)
        Thr.lock.acquire()
        Thr.outputs[self.id] = output
        Thr.lock.release()
