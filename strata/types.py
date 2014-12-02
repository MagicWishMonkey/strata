import inspect
# from types import *
from datetime import datetime


class IModel(object):
    __repository__ = None

    @property
    def repository_class(self):
        return self.__repository__


class IRepository(object):
    __model__ = None

    @property
    def model_class(self):
        return self.__model__


class MetaModel(type):
    def __new__(meta, name, bases, dct):
        return super(MetaModel, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        if name != "Model":
            TypeTable.register(cls)

        super(MetaModel, cls).__init__(name, bases, dct)

    @staticmethod
    def find(name):
        models = TypeTable.__models__
        try:
            return models[name.lower().title()]
        except:
            return None


class MetaRepository(type):
    def __new__(meta, name, bases, dct):
        return super(MetaRepository, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        if name != "Repository":
            TypeTable.register(cls)

        super(MetaRepository, cls).__init__(name, bases, dct)



class TypeTable:
    __table__ = {}
    __models__ = {}
    __repositories__ = {}

    @staticmethod
    def register(cls):
        name = cls.__name__
        tbl = TypeTable.__table__
        tbl[name] = cls

        try:
            meta_type = cls.__metaclass__
            #o = cls()
            if meta_type is MetaModel:#isinstance(meta_type, MetaModel) is True:
                TypeTable.__models__[name] = cls
                try:
                    repositories = TypeTable.__repositories__
                    repository_name = name
                    if repository_name.endswith("s") is False:
                        repository_name = "%ss" % repository_name

                    repository = repositories[repository_name]
                    repository.__model__ = cls
                    cls.__repository__ = repository

                    #repositories[repository_name].__model__ = cls
                except:
                    pass
            elif meta_type is MetaRepository:#if isinstance(meta_type, MetaRepository) is True:
                TypeTable.__repositories__[name] = cls
                try:
                    models = TypeTable.__models__
                    model_name = name
                    if model_name.endswith("s"):
                        model_name = model_name[0:len(model_name) - 1]

                    model = models[model_name]
                    model.__repository__ = cls
                    cls.__model__ = model
                except:
                    pass
        except:
            pass

    @staticmethod
    def models():
        tbl = TypeTable.__models__
        models = tbl.values()
        return models


    @staticmethod
    def repositories():
        tbl = TypeTable.__repositories__
        repositories = tbl.values()
        return repositories




def is_string(o):
    """Returns True if the specified type is a string, False otherwise
    >>> is_string("Ron")
    True
    >>> is_string(5)
    False
    """
    return True if isinstance(o, basestring) else False


def not_string(o):
    """Returns True if the specified type is not a string, True otherwise
    >>> not_string("Ron")
    False
    >>> not_string(5)
    True
    """
    return False if isinstance(o, basestring) else True


def is_list(o):
    """Returns True if the specified type is a list, False otherwise
    >>> is_list([1, 2, 3])
    True
    >>> is_list("Ron")
    False
    """
    return True if isinstance(o, list) else False


def not_list(o):
    """Returns True if the specified type is not a list, True otherwise
    >>> not_list([1, 2, 3])
    False
    >>> not_list("Ron")
    True
    """
    return False if isinstance(o, list) else True


def is_tuple(o):
    """Returns True if the specified type is a tuple, False otherwise
    >>> is_tuple(("Ron","Monkey","Catcher"))
    True
    >>> is_tuple("Ron")
    False
    """
    return True if isinstance(o, tuple) else False


def not_tuple(o):
    """Returns True if the specified type is not a tuple, False otherwise
    >>> not_tuple(("Ron","Monkey","Catcher"))
    False
    >>> not_tuple("Ron")
    True
    """
    return False if isinstance(o, tuple) else True


def is_dict(o):
    """Returns True if the specified type is a dict, False otherwise
    >>> is_dict({"Name": "Ron"})
    True
    >>> is_dict("Ron")
    False
    """
    return True if isinstance(o, dict) else False


def not_dict(o):
    """Returns True if the specified type is not a dict, False otherwise
    >>> not_dict({"Name": "Ron"})
    False
    >>> not_dict("Ron")
    True
    """
    return False if isinstance(o, dict) else True


def is_date(o):
    """Returns True if the specified type is a datetime, False otherwise
    >>> is_date(datetime.datetime.now())
    True
    >>> is_date("Ron")
    False
    """
    return True if isinstance(o, datetime) else False


def not_date(o):
    """Returns True if the specified type is not a datetime, False otherwise
    >>> not_date(datetime.datetime.now())
    False
    >>> not_date("Ron")
    True
    """
    return False if isinstance(o, datetime) else True


def is_num(o):
    """Returns True if the specified type is a numeric type, False otherwise
    >>> is_num(1)
    True
    >>> is_num("Ron")
    False
    """
    return True if isinstance(o, (int, long, float, complex)) else False


def not_num(o):
    """Returns True if the specified type is not a numeric type, True otherwise
    >>> not_num(1)
    False
    >>> not_num("Ron")
    True
    """
    return False if isinstance(o, (int, long, float, complex)) else True


def is_int(o):
    """Returns True if the specified type is a integer, False otherwise
    >>> is_int(1)
    True
    >>> is_int("Ron")
    False
    >>> is_int(.5)
    False
    """
    return True if isinstance(o, int) else False


def not_int(o):
    """Returns True if the specified type is not a integer, True otherwise
    >>> not_int(1)
    False
    >>> not_int("Ron")
    True
    >>> not_int(.5)
    True
    """
    return False if isinstance(o, int) else True


def is_long(o):
    """Returns True if the specified type is a long, False otherwise
    >>> is_long(1240832864000L)
    True
    >>> is_long("Ron")
    False
    >>> is_long(1)
    False
    >>> is_long(.5)
    False
    """
    return True if isinstance(o, long) else False


def not_long(o):
    """Returns True if the specified type is not a long, True otherwise
    >>> not_long(1240832864000L)
    False
    >>> not_long("Ron")
    True
    >>> not_long(1)
    True
    >>> not_long(.5)
    True
    """
    return False if isinstance(o, long) else True


def is_class(o):
    """Returns True if the specified type is a class type, False otherwise
    >>> is_class("".__class__)
    True
    >>> is_class("Ron")
    False
    """
    return True if inspect.isclass(o) else False


def not_class(o):
    """Returns True if the specified type is not a class type, False otherwise
    >>> not_class("".__class__)
    False
    >>> not_class("Ron")
    True
    """
    return False if inspect.isclass(o) else True


def is_blank(o):
    """Returns True if the specified instance is null,
    or if it's a string type with length=0, or if it's
    a list/tuple/dict type with length = 0
    >>> is_blank("")
    True
    >>> is_blank(None)
    True
    >>> is_blank([])
    True
    >>> is_blank(5)
    False
    >>> is_blank("Ron")
    False
    >>> is_blank(["Ron"])
    False
    """

    if not o:
        return True

    if isinstance(o, basestring):
        return True if len(o) == 0 else False
    elif isinstance(o, (list, tuple)):
        return True if len(o) == 0 else False
    #elif isinstance(o, dict):
     #   return True if len(o) == 0 else False

    return False


def not_blank(o):
    """Returns True if the specified instance is not null,
    or if it's a string type with length > 0, or if it's
    a list/tuple/dict type with length > 0
    >>> not_blank("")
    False
    >>> not_blank(None)
    False
    >>> not_blank([])
    False
    >>> not_blank(5)
    True
    >>> not_blank("Ron")
    True
    >>> not_blank(["Ron"])
    True
    """
    return False if is_blank(o) else True


def is_function(o):
    """Returns True if the specified type is a function type
    >>> is_function(inspect.isclass)
    True
    >>> is_function("Ron")
    False
    """

    #lst = (__types__.MethodType, __types__.FunctionType, __types__.ModuleType)
    #lst = (MethodType, FunctionType, ModuleType)
    # return True if isinstance(o, lst) else False

    print "TODO: Fix the type checker"
    return False


def is_string(o):
    """Returns True if the specified type is a string"""
    return True if isinstance(o, basestring) else False


def not_string(o):
    """Returns True if the specified type is not a string"""
    return False if isinstance(o, basestring) else True


def is_list(o):
    """Returns True if the specified type is a list"""
    return True if isinstance(o, list) else False


def not_list(o):
    """Returns True if the specified type is not a list"""
    return False if isinstance(o, list) else True


def is_num(o):
    """Returns True if the specified type is a numeric type"""
    return True if isinstance(o, (int, long, float, complex)) else False


def not_num(o):
    """Returns True if the specified type is not a numeric type"""
    return False if isinstance(o, (int, long, float, complex)) else True





def parse_int(o):
    if o is None:
        return None

    try:
        return int(o)
    except:
        if isinstance(o, int):
            return o
        return None


def parse_bool(o):
    if o is None:
        return False
    if isinstance(o, bool):
        return o
    elif isinstance(o, int) is True:
        return False if o == 0 else True

    if isinstance(o, basestring):
        val = o.strip().lower()
        if val == "true" or val == "1":
            return True
    return False


def is_model(o):
    try:
        return True if isinstance(o, IModel) is True else False
    except:
        return False

