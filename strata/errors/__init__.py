#from fuze.errors.fuze_error import FuzeError
import datetime

class FuzeError(Exception):
    def __init__(self, *args, **kwd):
        Exception.__init__(self)

        message, inner = None, None
        for arg in args:
            if isinstance(arg, basestring) is True:
                message = arg
            elif isinstance(arg, Exception) is True:
                inner = arg

        if inner is None:
            inner = kwd.get("inner", kwd.get("ex", None))

        if message is None:
            if inner is not None:
                message = inner.message
            if message is None:
                message = kwd.get("message", "An error occurred.")

        self.message = message
        self.inner = inner
        self.timestamp = datetime.timestamp()