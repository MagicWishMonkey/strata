

class Enum(object):
    def __init__(self, *name, **kwd):
        self.name = name[0] if len(name) > 0 else kwd.get("name", None)
        if self.name is None:
            self.name = "Enum"
        elif kwd.get("name", None) is not None:
            kwd.pop("name")

        for key in kwd:
            val = kwd[key]
            self.__dict__[key] = val

    def clone(self, **overwrite):
        cpy = self.__class__(self.name)
        a, b = self.__dict__, cpy.__dict__
        for key in a:
            val = a[key]
            b[key] = val

        for key in overwrite:
            val = overwrite[key]
            b[key] = val
        return cpy

    def lower(self):
        return self.__str__().lower()

    def __eq__(self, other):
        try:
            if self.name == other.name:
                return True
            return False
        except:
            pass

        try:
            if other.strip().lower() == self.name.lower():
                return True
            return False
        except:
            return False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()


# class Enumerator(object):
#     @classmethod
#     def resolve(cls, key):
#         #cache = EnumeratorCache.get_cache()
#         cache = Enumerator.extract(cls).lookup
#         if isinstance(key, basestring):
#             key = key.strip().lower()
#         elif isinstance(key, int) is False:
#             if hasattr(key, "is_enum"):
#                 return key
#         e = cache.get(key, None)
#
#         return e
#
#     @staticmethod
#     def extract(cls):
#         if hasattr(cls, "enums"):
#             return cls
#
#         vars = Reflect.get_static_methods(cls)
#         tbl = {}
#         lst = []
#         for key in vars.keys():
#             if key == "resolve" or key == "prep" or key == "instance":
#                 continue
#             val = vars[key]
#             if isinstance(val, basestring):
#                 val = Enum(name=val, code=len(lst))
#             elif isinstance(val, Enum):
#                 if isinstance(val.name, int):
#                     val.code = val.name
#                     val.name = key
#                     code = val.code
#                 elif val.name is None:
#                     val.name = key
#             else:
#                 continue
#
#             if tbl.get(key.lower(), None) is None:
#                 if val.default:
#                     cls.default = val
#
#                 tbl[key.lower()] = val
#                 tbl["%ss" % key.lower()] = val#include plural spelling
#                 if val.code:
#                     tbl[val.code] = val
#                 lst.append(val)
#
#             #        for key in vars.keys():
#             #            if key == "resolve" or key == "prep" or key == "instance":
#             #                continue
#             #            val = vars[key]
#             #            code = val if isinstance(val, int) else None
#             #
#             #            if isinstance(val, Enum):
#             #                if isinstance(val.name, int):
#             #                    val.code = val.name
#             #                    val.name = key
#             #                    code = val.code
#             #                elif val.name is None:
#             #                    val.name = key
#             #            else:
#             #                val = Enum(key, val)
#             #
#             #            if val.default:
#             #                cls.default = val
#             #
#             #            tbl[key.lower()] = val
#             #            if code:
#             #                tbl[code] = val
#
#         vars = tbl
#         cache = EnumeratorCache.get_cache()
#         cache[cls] = tbl
#         cls.enums = lst
#         cls.lookup = tbl
#         return cls
#
#     @classmethod
#     def inspect(cls):
#         return Enumerator.extract(cls)
#
#     @classmethod
#     def list(cls):
#         return cls.inspect().enums