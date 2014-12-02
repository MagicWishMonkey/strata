import time
from datetime import datetime




class Stopwatch:
    __slots__ = ["start_ticks", "stop_ticks", "start_ts", "stop_ts", "flag"]

    def __init__(self):
        self.flag = 0
        self.start_ticks = time.time()
        self.start_ts = datetime.now()
        self.stop_ticks = 0
        self.stop_ts = None

    def start(self):
        if self.flag == None:
            print "The stopwatch is frozen."
            return self
        self.flag = 0
        self.start_ticks = time.time()
        self.start_ts = datetime.now()
        self.stop_ticks = 0
        self.stop_ts = None
        return self

    def stop(self):
        if self.flag == None:
            print "The stopwatch is frozen."
            return self

        self.flag = 1
        self.stop_ticks = time.time()
        self.stop_ts = datetime.now()
        return self

    def reset(self):
        if self.flag == None:
            print "The stopwatch is frozen."
            return self

        self.flag = 0
        self.start_ticks = time.time()
        self.start_ts = datetime.now()
        self.stop_ticks = 0
        self.stop_ts = None
        return self

    def rewind(self, ticks):
        self.start_ticks = (self.start_ticks - ticks)
        return self

    def offset(self, ticks):
        self.start_ticks = (self.start_ticks + ticks)
        return self

    def freeze(self):
        if self.flag == None:
            print "The stopwatch is frozen."
            return self

        self.flag = None
        self.stop_ticks = time.time()
        self.stop_ts = datetime.now()
        return self

    def elapsed(self, precision=4):
        start = self.start_ticks
        stop = time.time() if self.flag == 0 else self.stop_ticks
        #stop = self.stop_ticks if self.flag == 1 else ticks()
        diff = (stop - start)
        diff = round(diff, precision)
        return diff

    def average(self, count, precision=3):
        assert count is not None, "The count parameter is null!"
        time = self.elapsed()
        if count <= 1:
            return time

        avg = (time / float(count))
        try:
            avg = round(avg, precision)
        except:
            avg = round(avg, 3)

        return avg

    def sleep_until(self, milliseconds=0, seconds=0):
        if seconds > 0:
            while self.seconds < seconds:
                time.sleep(.05)
            return self

        if milliseconds > 0:
            while self.milliseconds < milliseconds:
                time.sleep(.05)
            return self
        return self

    @property
    def milliseconds(self):
        return self.elapsed()

    @property
    def seconds(self):
        time = self.elapsed()
        secs = round(time, 1)
        return secs

    def trace_average(self, count, precision=3):
        txt = self.emit_average(count, precision=precision)
        txt = self._format_pretty(txt)
        #sys.stdout.write(txt + "\n")
        return txt

    def __str__(self):
        #return self.emit()
        return "%s milliseconds" % str(self.milliseconds)

    def __repr__(self):
        return self.__str__()


    @staticmethod
    def create():
        return Stopwatch()

