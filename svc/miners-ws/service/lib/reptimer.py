from threading import Timer,Thread,Event
import os, time
import logger

logger = logger.instance(__name__, os.environ.get('LOG_REPTIMER', 'ERROR'))

class RepeatedTimer(object):

    def __init__(self, interval, function, args=[]):
        self.interval = interval
        self.function = function
        self.args     = args
        self.started  = False

    def start(self):
        if not self.started:
            self.started  = True
            self.thread   = Timer(self.interval,self.handle_function)
            self.thread.start()

    def stop(self):
        if self.started:
            self.started = False
            self.thread.cancel()

    def handle_function(self):
        self.function(*self.args)
        self.thread = Timer(self.interval,self.handle_function)
        self.thread.start()

if __name__ == '__main__':

    def action(t):
        print ("running ({})".format(t))

    timer = RepeatedTimer(1.0, action, ["test"])
    timer.start()
    print("S T A R T E D")
    time.sleep(5)
    print("T E R M I N A T I N G")
    timer.stop()
