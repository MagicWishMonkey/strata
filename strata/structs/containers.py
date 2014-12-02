from types import ModuleType


class SelfWrapper(ModuleType):
    def __init__(self, self_module, baked_args={}, label=None):
        # this is super ugly to have to copy attributes like this,
        # but it seems to be the only way to make reload() behave
        # nicely.  if i make these attributes dynamic lookups in
        # __getattr__, reload sometimes chokes in weird ways...
        for attr in ["__builtins__", "__doc__", "__name__", "__package__"]:
            setattr(self, attr, getattr(self_module, attr, None))

        # python 3.2 (2.7 and 3.3 work fine) breaks on osx (not ubuntu)
        # if we set this to None.  and 3.3 needs a value for __path__
        self.__path__ = []
        self.self_module = self_module
        self.__readonly__ = False

        if label is None:
            label = self_module.__name__
            try:
                if self.self_module.__class__.__name__ != "module":
                    label = self.self_module.__class__.__name__
            except:
                pass

        self.__label__ = label




    def seal(self):
        """
        Make the wrapper read only, will throw an exception
        when an attribute is assigned or updated.
        """
        self.__readonly__ = True
        return self


    def __setattr__(self, name, value):
        if hasattr(self, "__readonly__"):
            if self.__readonly__ is True:
               raise Exception("This wrapper is marked as read only, it cannot be updated.")

        ModuleType.__setattr__(self, name, value)

    # def __getattr__(self, name):
    #     #if name == "env": raise AttributeError
    #     return self.__attrs__[name]

    # accept special keywords argument to define defaults for all operations
    # that will be processed with given by return SelfWrapper
    def __call__(self, **kwargs):
        return SelfWrapper(self.self_module, kwargs)

    def __repr__(self):
        label = None
        try:
            label = self.__label__
        except:
            pass

        if label is None:
            label = "SelfWrapper"
        return label

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
            return o
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            pass

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



class Flags(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            try:
                k = key.strip().lower()
                if k == key:
                    return False
                for key in self:
                    if key.strip().lower() == k:
                        return self[key]
                return False
            except:
                pass
            return False

    def __setattr__(self, key, value):
        flag = Flags.parse_bool(value)
        self[key] = flag

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            pass

    def clone(self):
        return self.copy()

    def bind(self, **kwd):
        if len(kwd) > 0:
            for k in kwd:
                v = kwd[k]
                self[k] = Flags.__parse_bool__(v)
        return self

    @staticmethod
    def __parse_bool__(val):
        if val is True:
            return True
        if val == 1:
            return True
        if isinstance(val, basestring) is True:
            txt = val.strip().lower()
            if txt == "y" or txt == "yes":
                return True
            if txt == "1" or txt == "true":
                return True
            return False
        return False

    @staticmethod
    def create(*args, **kwd):
        flags = Flags()
        if args:
            for arg in args:
                if isinstance(arg, (list, tuple)) is True and len(arg) > 1:
                    k, v = arg[0], arg[1]
                    if isinstance(k, basestring) is True:
                        flags[k] = Flags.__parse_bool__(v)

        if args and len(args) > 0:
            return Wrapper(args[0])
        if len(kwd) > 0:
            for k in kwd:
                v = kwd[k]
                flags[k] = Flags.__parse_bool__(v)
        return flags


    def __str__(self):
        buffer = []
        for k in self:
            v = self[k]
            buffer.append("%s=%s" % (str(k), str(v)))
        txt = "&".join(buffer)
        return txt

    def __repr__(self):
        return self.__str__()