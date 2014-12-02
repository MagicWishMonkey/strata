import time
from threading import Lock


class Buffer(object):
    def __init__(self):
        self.__list__ = []
        self.__lock__ = Lock()
        self.__loading__ = False

    def consume(self, source, adapter=None, chunked=False):
        self.__loading__ = True
        try:
            for o in source:
                if adapter is not None:
                    o = adapter(o)

                if chunked is True:
                    self.extend(o)
                else:
                    self.put(o)
        except Exception, ex:
            message = "Error loading buffer-> %s" % ex.message
            raise Exception(message, ex)
        finally:
            self.__loading__ = False

    def extend(self, values):
        with self.__lock__:
            self.__list__.append(values)
        return self

    def append(self, value):
        with self.__lock__:
            if isinstance(value, list) is True:
                map(self.__list__.append, value)
            else:
                self.__list__.append(value)

        return self

    def set(self, value):
        return self.append(value)

    def get(self):
        with self.__lock__:
            try:
                o = self.__list__.pop()
                return o
            except:
                return None

    def pop(self):
        return self.get()

    def __iter__(self):
        return self.next()

    def next(self):
        while True:
            # if self.empty is True:
            #     if self.__loading__ is True:
            #         time.sleep(.01)
            #         continue
            #     break

            o = self.pop()
            if o is None and self.empty is True:
                if self.__loading__ is True:
                    time.sleep(.01)
                    continue
                break

            yield o


    @property
    def list(self):
        return self.__list__

    @classmethod
    def create(cls):
        return cls()

    def __repr__(self):
        return "Buffer#{cnt}".format(cnt=self.__len__())

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.__list__)

    @property
    def empty(self):
        cnt = len(self.__list__)
        return True if cnt == 0 else False



class Pipeline(object):
    def __init__(self, fn):
        self.fn = fn
        self.endpoint = None

    def connect(self, fn):
        if self.endpoint is not None:
            return self.endpoint.connect(fn)
            #raise Exception("An endpoint has already been connected!")
        pipeline = Pipeline(fn)#, self.output)
        self.endpoint = pipeline

    def pump(self, o):
        v = self.fn(o)
        if self.endpoint is not None:
            return self.endpoint.pump(v)
        return v

    def process(self, inputs, *outputs):
        if len(outputs) == 0:
            return map(self.pump, inputs)

        outputs = outputs[0]
        pump = self.pump
        for a in inputs:
            b = pump(a)
            outputs.append(b)
        return outputs

    def multiplex(self, inputs, worker_count=2):
        from strata import util

        cnt = len(inputs)
        outputs = Buffer.create()
        for x in xrange(worker_count):
            util.dispatch(self.process, inputs, outputs)

        self.process(inputs, outputs)
        while inputs.empty is False:
            util.sleep(.01)
        while len(outputs) < cnt:
            util.sleep(.01)

        return outputs.list


    def __repr__(self):
        return "Pipeline"

    def __str__(self):
        return self.__repr__()



class Wrapper(dict):
    """
    A Wrapper object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.
        >>> o = Wrapper(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'
    """

    # def get(self, key, **kwd):
    #     try:
    #         return self[key]
    #     except:
    #         if kwd.keys() > 0:
    #             try:
    #                 return kwd["default"]
    #             except:
    #                 pass
    #         raise AttributeError("Unable to get the wrapper attribute %s-> " % key)

    # def __getattr__(self, method):
    #     fn = getattr(self.o, method)
    #     return fn

    # def __getitem__(self, item):
    #     return None


    # def override(self, other):
    #     def override(a, b):
    #         keys = b.keys()
    #         for key in keys:
    #             o = b[key]
    #             if isinstance(o, dict) is True:
    #                 i = a[key]
    #                 for k in o.keys():
    #                     i[k] = o[k]
    #             else:
    #                 a[key] = o
    #
    #     override(self, other)
    #     return self

    def override(self, other):
        def override(a, b):
            keys = b.keys()
            for key in keys:
                o = b[key]
                if isinstance(o, dict) is True:
                    try:
                        i = a[key]
                        for k in o.keys():
                            i[k] = o[k]
                    except KeyError:
                        a[key] = o
                else:
                    a[key] = o

        override(self, other)
        return self

    def __getattr__(self, key):
        try:
            o = self[key]
            if isinstance(o, dict) is True:
                if isinstance(o, Wrapper) is False:
                    o = Wrapper.create(o)
                    self[key] = o

                    #return Wrapper.create(o)
            return o
        except KeyError, ex:
            return None
            #raise AttributeError("Unable to get the wrapper attribute %s-> %s" % (key, ex.message))

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, ex:
            raise AttributeError("Unable to delete the wrapper attribute %s-> %s" % (key, ex.message))

    def reduce(self, fn=None):
        obj = {}
        keys = self.keys()
        for key in keys:
            v = self[key]
            if isinstance(v, list) and len(v) > 0 and hasattr(v[0], "reduce"):
                for x in xrange(len(v)):
                    v[x] = v[x].reduce()

            obj[key] = v
        if fn:
            return fn(obj)
        return obj

    def clone(self):
        return Wrapper(self.copy())

    def __repr__(self):
        return '<Wrapper ' + dict.__repr__(self) + '>'

    @staticmethod
    def create(*args, **kwargs):
        if args and len(args) > 0:
            return Wrapper(args[0])
        return Wrapper(kwargs)


class SafeWrapper(Wrapper):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def clone(self):
        return SafeWrapper(self.copy())
