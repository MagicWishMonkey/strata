import uuid
import hashlib
import time
import threading



class Worker(object):
    def __init__(self, fn):
        self.uuid = "Worker#{uuid}".format(uuid=hashlib.md5(str(uuid.uuid4())).hexdigest()[0:10])
        self.fn = fn
        self.thread = None
        self.running = False
        self.complete = False
        self.result = None


        self.thread = threading.Thread(target=self.__run__, name=self.uuid)
        self.thread.setDaemon(True)

    def __run__(self):
        self.running = True
        fn = self.fn
        try:
            self.result = fn()
        except Exception, ex:
            message = "Error executing thread function: %s" % ex.message
            print message
            self.result = Exception(message, ex)
        finally:
            self.running = False
            self.complete = True
            self.thread = None

    def start(self):
        if self.running is True or self.thread is None:
            print "This thread has already been run!"
            return self

        self.running = True
        self.thread.start()
        return self

    def join(self):
        return self.abort()

    def abort(self):
        if self.thread is None:
            return self

        try:
            self.thread.join()
        except:# Exception, ex:
            pass
        self.thread = None
        self.running = False
        self.complete = False
        return self

    @property
    def failed(self):
        return True if isinstance(self.result, Exception) is True else False

    def __str__(self):
        if self.complete is False:
            return "Worker#%s [INCOMPLETE]" % self.uuid
        return "Worker#%s [COMPLETE]" % self.uuid

    def __repr__(self):
        return self.__str__()

    @classmethod
    def create(cls, fn):
        return cls(fn)

    @classmethod
    def launch(cls, fn):
        worker = cls(fn)
        return worker.start()
