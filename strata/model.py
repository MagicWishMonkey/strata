import datetime
from strata import *
from strata.types import IModel
from strata.types import MetaModel
# from fuze.types import TypeTable



# class MetaModel(type):
#     def __new__(meta, name, bases, dct):
#         return super(MetaModel, meta).__new__(meta, name, bases, dct)
#
#     def __init__(cls, name, bases, dct):
#         if name != "Model":
#             TypeTable.register(cls)
#
#         super(MetaModel, cls).__init__(name, bases, dct)


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

    # @staticmethod
    # def restore(data):
    #     obj = util.unjson(data)
    #     uri = obj["_"]
    #     type = uri.split("#")[0]
    #     cls = MetaModel.find(type)
    #     model = cls(**(obj))
    #     return model

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
        # type = self.__class__.__name__
        # id, label = None, None
        # try:
        #     id = self.id
        # except:
        #     pass
        #
        # try:
        #     label = self.label
        # except:
        #     pass
        #
        # if id is not None or label is not None:
        #     if id is not None and label is not None:
        #         return "%s#%s [%s]" % (type, str(id), label)
        #     elif id is not None:
        #         return "%s#%s" % (type, str(id))
        #     else:
        #         return "%s [%s]" % (type, label)
        #
        # return type

    def __repr__(self):
        return self.__str__()


# class Member(Model):
#     __slots__ = [
#         "id",
#         "label"
#     ]

