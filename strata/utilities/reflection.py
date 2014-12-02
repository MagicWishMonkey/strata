import new
import uuid
import types
import hashlib
import inspect





class Reflector:

    @staticmethod
    def rcurry(f, *a, **kw):
        def curried(*more_a, **more_kw):
            return f(*(more_a + a), **dict(kw, **more_kw))
        return curried

    @staticmethod
    def curry(f, *a, **kw):
        def curried(*more_a, **more_kw):
            return f(*(a + more_a), **dict(kw, **more_kw))
        return curried

    def compile(self, script):
        def indent(txt):
            padding = "    "
            lines = txt.split("\n")
            if len(lines) == 1:
                txt = "%s%s" % (padding, txt)
                return txt

            for x, l in enumerate(lines):
                lines[x] = "%s%s" % (padding, l)
            txt = "\n".join(lines)
            return txt

        method = None
        lines = script.split("\n")
        for line in lines:
            if line.strip().startswith("def "):
                parts = line.strip().split(" ")
                method = parts[1].split("(")[0]
                break

        if method is None:
            if script.startswith("lambda "):
                method = "run"
                script = "run = %s" % script

        buffer = []
        if method is None:
            buffer.append("def run():")
            buffer.append(indent(script))
        else:
            buffer.append(script)
            buffer.append("run = %s" % method)

        script = "\n".join(buffer)
        print script

        def __compile__(code, name, add_to_sys_modules=False):
            module = new.module(name)
            if add_to_sys_modules:
                import sys
                sys.modules[name] = module
            exec code in module.__dict__
            return module

        name = "tmp_{uuid}".format(uuid=hashlib.md5(str(uuid.uuid1())).hexdigest())
        code = __compile__(script, name, add_to_sys_modules=False)
        return code.run



    # @staticmethod
    # def get_method(o, signature):
    #     method = getattr(o, signature)
    #     if method is not None:
    #         return method
    #
    #     for name, method in inspect.getmembers(o, inspect.ismethod):
    #         if name == signature:
    #             return method
    #     return None
    #
    # @staticmethod
    # def trace(o):
    #     """Print out the methods and properties of the object instance."""
    #     methods = Reflect.get_methods(o)
    #     for method in methods:
    #         methodName = method[0]
    #         print methodName
    #
    # @staticmethod
    # def get_methods(o):
    #     methods = inspect.getmembers(o, inspect.ismethod)
    #     functions = inspect.getmembers(o, inspect.isfunction)
    #     if len(functions) > 0:
    #         methods.extend(functions)
    #     return methods
    #
    # @staticmethod
    # def get_public_methods(o):
    #     methods = inspect.getmembers(o, inspect.ismethod)
    #     filtered = [(name, method) for (name, method) in methods if(name[0] != "_")]
    #     return filtered
    #
    # @staticmethod
    # def get_private_methods(o):
    #     methods = inspect.getmembers(o, inspect.ismethod)
    #     filtered = [(name, method) for (name, method) in methods if(name[0] == "_")]
    #     return filtered
    #
    # @staticmethod
    # def patch(o, methods):
    #     for method in methods:
    #         name = method.func_name
    #         fn = types.MethodType(method, o)
    #         setattr(o, name, fn)
    #     return o
    #
    # @staticmethod
    # def get_static_methods(cls):
    #     lst = cls.mro()
    #     tbl = {}
    #     for attr in lst:
    #         d = attr.__dict__
    #         for k in d.keys():
    #             if k.startswith("_"):
    #                 continue
    #             v = d[k]
    #             tbl[k] = v
    #     return tbl
    #
    # @staticmethod
    # def get_module_classes(name):
    #     classes = inspect.getmembers(sys.modules[name], inspect.isclass)
    #     return classes
    #
    # @staticmethod
    # def is_base_class(cls, base):
    #     if hasattr(cls, "__bases__") is False:
    #         return False
    #
    #     bases = cls.__bases__
    #     return True if len([b for b in bases if isinstance(b, base)]) > 0 else False
    #
    #
    # @staticmethod
    # def get_frame(offset=0):
    #     frame = sys._getframe(offset + 1)
    #     file = frame.f_code.co_filename
    #     line = frame.f_lineno
    #     func = frame.f_code.co_name
    #     vars = frame.f_locals
    #     module = None
    #     if vars is not None:
    #         try:
    #             vars = vars["self"]
    #             module = vars.__class__.__name__
    #             func = "%s.%s()" % (module, func)
    #         except KeyError:
    #             pass
    #
    #     #rel = os.path.basename(file)
    #     #label = "%s/%s %s()" % (rel, line, func)
    #     o = {
    #         "line": line,
    #         "file": file,
    #         "function": func,
    #         "module": module
    #     }
    #     return o



# def curry(f, *a, **kw):
#     def curried(*more_a, **more_kw):
#         return f(*(a + more_a), **dict(kw, **more_kw))
#     return curried
#
#
# def frame_scan(offset=1):
#     frame = inspect.currentframe().f_back
#     while offset > 0:
#         offset = (offset - 1)
#         frame = frame.f_back
#     return frame
#
#
# def caller(offset=0):
#     try:
#         frame = frame_scan(offset=(2 + offset))
#         return frame.f_locals.self
#     except Exception, ex:
#         print "Unable to locate caller-> %s" % ex.message
#         return None
#
#
#
# def stack(offset=0):
#     frame, object, class_name = None, None, None
#     try:
#         frame = frame_scan(offset=(2 + offset))
#     except Exception, ex:
#         print "Unable to locate caller-> %s" % ex.message
#         return None
#
#     try:
#         object = frame.f_locals["self"]
#         try:
#             class_name = object.__class__.__name__
#         except Exception, e:
#             print "Unable to get the class name-> %s" % e.message
#     except Exception, ex:
#         print "Unable to get the callerobject-> %s" % ex.message
#
#     method, file, line = None, None, None
#
#     line = frame.f_lineno
#     code = frame.f_code
#     if code is not None:
#         file = code.co_filename
#         method = code.co_name
#
#     location = {
#         "class": class_name,
#         "method": method,
#         "file": file,
#         "line": line
#     }
#     stack = {
#         "caller": object,
#         "location": location
#     }
#     return stack
#
#
