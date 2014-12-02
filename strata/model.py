import datetime
from strata import *
from strata.types import IModel
from strata.types import MetaModel



class Model(IModel):
    __metaclass__ = MetaModel
    __slots__ = []

    def __init__(self, **kwd):
        self.bind(**kwd)

    def bind(self, **kwd):
        cls = self.__class__
        slots = cls.__slots__
        cnt = len(slots)
        setter = self.__setattr__
        #defaults = cls.defaults
        defaults = {}
        for x in xrange(cnt):
            slot = slots[x]
            val = kwd.get(slot, defaults.get(slot, None))
            setter(slot, val)


    def objectify(self):
        table = {}
        slots = self.__slots__
        cnt = len(slots)
        getter = self.__getattribute__
        for x in xrange(cnt):
            slot = slots[x]
            val = getter(slot)
            table[slot] = val
        return table

    def deflate(self):
        return self.objectify()

    def serialize(self):
        obj = self.objectify()
        obj["_"] = self.uri
        try:
            return util.json(obj)
        except Exception, ex:
            fixed = False
            for key in obj:
                val = obj[key]
                if isinstance(val, datetime):
                    fixed = True
                    val = val.strftime("%Y-%m-%d %H:%M:%S")
                    obj[key] = val
            if fixed is True:
                return util.json(obj)

            raise ex

    @property
    def model_type(self):
        return self.__class__.__name__

    @classmethod
    def create(cls, *args, **kwd):
        if len(args) > 0 and len(kwd) == 0:
            if len(args) == 1 and isinstance(args[0], list) is False:
                return cls(**(args[0]))

            args = util.unroll(args)
            lst = []
            for o in args:
                m = cls(**(o))
                lst.append(m)
            return lst

        try:
            return cls(**kwd)
        except Exception, ex:
            raise ex

    @property
    def ctx(self):
        return util.context()

    @property
    def repository(self):
        cls = self.repository_class
        return cls(self.ctx)

    @property
    def uri(self):
        return self.repository_class.gen_uri(self)

    def __str__(self):
        return self.uri

    def __repr__(self):
        return self.__str__()

