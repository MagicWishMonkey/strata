from __future__ import print_function
import os
import sys

try:
    import readline  # import readline if not running on windows
    readline.get_history_length()  # redundant, prevents unused import warn
except:
    pass


class __Wrapper__(dict):
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
                if isinstance(o, __Wrapper__) is False:
                    o = __Wrapper__.create(o)
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
        return __Wrapper__(self.copy())

    def __repr__(self):
        return '<Wrapper ' + dict.__repr__(self) + '>'

    @staticmethod
    def create(*args, **kwargs):
        if args and len(args) > 0:
            return __Wrapper__(args[0])
        return __Wrapper__(kwargs)


class __Terminal__(object):
    __colors__ = None
    __colorama__ = False

    def __init__(self):
        self.colors = __Terminal__.__colors__
        self.padding = None
        self.buffer = []
        if self.colors is None:
            colors = __Wrapper__({
                "ul": "",
                "white": "",
                "red": "",
                "green": "",
                "yellow": "",
                "blue": "",
                "pink": "",
                })

            try:
                from colorama import init as init_colorama, Fore, Style
                __Terminal__.__colorama__ = True
                colors.ul = "\x1b[%sm" * 3 % (2, 4, 33)
                colors.white = "\x1b[%sm" % 0
                cols = ["\x1b[%sm" % n for n in range(91, 96)]
                colors.red = cols[0]
                colors.green = cols[1]
                colors.yellow = cols[2]
                colors.blue = cols[3]
                colors.pink = cols[4]
            except ImportError:
                pass

            __Terminal__.__colors__ = colors
            self.colors = colors
            self.current = colors.white

    def clear(self):
        self.buffer = []
        return self

    def bind(self, color):
        if color is None:
            return self.write

        if color == "blue":
            self.current = self.colors.blue
            return self.blue
        elif color == "white":
            self.current = self.colors.white
        elif color == "red":
            self.current = self.colors.red
            return self.red
        elif color == "green":
            self.current = self.colors.green
            return self.green
        elif color == "yellow":
            self.current = self.colors.yellow
            return self.yellow
        elif color == "blue":
            self.current = self.colors.blue
            return self.blue
        elif color == "pink":
            self.current = self.colors.pink
            return self.pink
        return self.write

    def align(self, *message):
        if len(message) == 0:
            return ""

        buffer = []
        for msg in message:
            buffer.append(msg)
        msg = " ".join(buffer)
        if self.padding is None or self.padding == 0:
            return msg


    def ul(self, *message):
        self.current = self.colors.ul
        if len(message) == 0:
            return self
        return self.write(*message)

    def yellow(self, *message, **kwd):
        self.current = self.colors.yellow
        if len(message) == 0:
            return self
        return self.write(*message, **kwd)

    def red(self, *message):
        self.current = self.colors.red
        if len(message) == 0:
            return self
        return self.write(*message)

    def green(self, *message, **kwd):
        self.current = self.colors.green
        if len(message) == 0:
            return self
        return self.write(*message, **kwd)

    def blue(self, *message):
        self.current = self.colors.blue
        if len(message) == 0:
            return self
        return self.write(*message)

    def pink(self, *message):
        self.current = self.colors.pink
        if len(message) == 0:
            return self
        return self.write(*message)

    def white(self, *message):
        self.current = self.colors.white
        if len(message) == 0:
            return self
        return self.write(*message)

    def whitespace(self):
        print(self.colors.white)
        return self

    def newline(self, *count):
        count = count[0] if len(count) > 0 else 1
        if count is None:
            self.buffer.append("\n")
            return
        self.buffer.append("".join(["\n" for x in xrange(count)]))
        return self

    def write(self, *message, **kwd):
        flush = kwd.get("flush", True)
        if len(kwd) > 0:
            color = kwd.get("color", None)
            if color is not None:
                print("CHANGING COLOR TO %s" % color)

        buffer = self.buffer
        buffer.append(self.current)
        if self.padding is not None:
            if isinstance(self.padding, basestring) is False and self.padding > 0:
                padding = "".join([" " for x in xrange(self.padding)])
                txt = self.current
                lines = txt.split("\n")
                if len(lines) > 1:
                    for x, l in enumerate(lines):
                        line = "%s%s" % (padding, l)
                        lines[x] = line
                    txt = "\n".join(lines)
                    buffer = [txt]
                buffer.append(padding)

        for msg in message:
            if msg is None:
                msg = ""
            buffer.append(msg)
        buffer.append(self.colors.white)
        txt = "".join(buffer)
        if flush is True:
            self.buffer = []
            print(txt)
        return self

    def add_pad(self, *amt):
        amt = 1 if len(amt) == 0 else amt[0]
        cnt = self.padding
        if cnt is None:
            cnt = 0
        cnt = (cnt + amt)
        self.padding = cnt
        return self

    def rem_pad(self, *amt):
        amt = 1 if len(amt) == 0 else amt[0]
        cnt = self.padding
        if cnt is None:
            return self

        cnt = (cnt - amt)
        if cnt < 0:
            cnt = 0
        self.padding = cnt
        return self


class Console(object):
    def __init__(self):
        self.terminal = __Terminal__()
        self.debug_mode = False
        self.load()
        self.welcome()

    def load(self):
        pass

    def welcome(self):
        pass

    def goodbye(self):
        pass

    def prompt(self):
        return ">"

    def write(self, msg):
        self.terminal.white(msg)
        return self

    def trace(self, msg):
        self.terminal.blue(msg)
        return self

    def info(self, msg):
        self.terminal.green(msg)
        return self

    def notify(self, msg):
        self.terminal.yellow(msg)
        return self

    def newline(self, *cnt):
        cnt = 1 if len(cnt) == 0 or cnt[0] < 1 else cnt[0]
        for x in xrange(cnt):
            self.terminal.whitespace()
        return self

    def alert(self, msg):
        self.terminal.red(msg)
        return self

    def ask(self, message, cast=True):
        if message.endswith(" ") is False:
            message = "%s " % message

        sys.stdout.write(message)
        txt = sys.stdin.readline().replace("\n", "")
        if len(txt) == 0:
            return None
        if cast is False:
            return txt
        if txt.lower() == "y" or txt.lower() == "yes" or txt == "1":
            return True
        if txt.lower() == "n" or txt.lower() == "no" or txt == "0":
            return False
        return txt

    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)

    def __getitem__(self, command):
        try:
            return getattr(self, command.strip().lower())
        except:
            msg = "The command '%s' is not supported." % command
            raise Exception(msg)

    def exit(self):
        """ Exit the program. """
        self.terminal.clear()
        self.terminal.newline()
        self.terminal.red("shutting down.")
        sys.exit()


    def invoke(self, command):
        pass

    def read_loop(self):
        __read_input__ = raw_input
        callback = self.invoke
        while True:
            prompt = self.prompt()
            if prompt.endswith(" ") is False:
                prompt = "%s " % prompt
            try:
                input = __read_input__(prompt).strip()
                try:
                    callback(input)
                except Exception, ex:
                    message = "Error executing input: %s" % ex.message
                    self.alert(message)
            except (KeyboardInterrupt, EOFError):
                self.exit()
                return


                # import sys
# from .log import Terminal
#
#
# class Console(object):
#     def __init__(self):
#         self.terminal = Terminal()
#         self.debug_mode = False
#
#     def clear(self):
#         self.terminal.clear()
#         return self
#
#     def write(self, msg):
#         self.terminal.white(msg)
#         return self
#
#     def trace(self, msg):
#         self.terminal.blue(msg)
#         return self
#
#     def info(self, msg):
#         self.terminal.green(msg)
#         return self
#
#     def notify(self, msg):
#         self.terminal.yellow(msg)
#         return self
#
#     def alert(self, msg):
#         self.terminal.red(msg)
#         return self
#
#     def ask(self, message):
#         if message.endswith(" ") is False:
#             message = "%s " % message
#
#         sys.stdout.write(message)
#         txt = sys.stdin.readline().replace("\n", "")
#         if len(txt) == 0:
#             return None
#         if txt.lower() == "y" or txt.lower() == "yes" or txt == "1":
#             return True
#         if txt.lower() == "n" or txt.lower() == "no" or txt == "0":
#             return False
#         return txt
#
#     def __getitem__(self, command):
#         try:
#             return getattr(self, command.strip().lower())
#         except:
#             msg = "The command '%s' is not supported." % command
#             raise Exception(msg)
#
#     @classmethod
#     def invoke(cls):
#         fn, cmd = cls.prepare()
#
#         if fn is not None:
#             if cmd.debug_mode is True:
#                 cmd.terminal.pink("----------------------------------------------")
#                 cmd.terminal.pink("DEBUG MODE ENABLED")
#                 cmd.terminal.pink("----------------------------------------------")
#             try:
#                 fn()
#                 #print("...")
#             except Exception, ex:
#                 message = "Error invoking command: %s" % ex.message
#                 cmd.alert(message)
#
#     @classmethod
#     def parse(cls):
#         fn, cmd = cls.prepare()
#         return fn
#
#     @classmethod
#     def prepare(cls):
#         def curry(f, *a, **kw):
#             def curried(*more_a, **more_kw):
#                 return f(*(a + more_a), **dict(kw, **more_kw))
#             return curried
#
#         console = None
#         try:
#             console = cls()
#         except Exception, ex:
#             message = ex.message
#             Terminal().red(message)
#             return None, None
#
#
#         try:
#             console = cls()
#             txt = " ".join(sys.argv[1:])
#             #print(txt)
#             if txt.strip().endswith("-d"):
#                 txt = txt[0:len(txt) - 3]
#                 console.debug_mode = True
#                 #print(txt)
#
#             if txt.find(" -d ") > -1:
#                 txt = txt.replace(" -d ", " ").strip()
#                 console.debug_mode = True
#                 #print(txt)
#                 #if txt.find("tag=") > -1:
#                 #    txt = txt.replace(" -d ", " ")
#
#             parts = txt.split(" ")
#             command = parts[0]
#             args = " ".join(parts[1:])
#             if len(args) == 0 and command.find(":") > -1:
#                 parts = command.split(":")
#                 command = parts[0]
#                 args = " ".join(parts[1:])
#
#             function = None
#             try:
#                 function = console[command]
#             except:
#                 console.alert("The command could not be found: %s" % command)
#                 return None, None
#
#             #print(args)
#             if args is not None and len(args) > 0:
#                 # print("bind args...")
#                 function = curry(function, args)
#             return function, console
#         except Exception, ex:
#             msg = "The command could not be parsed! %s" % ex.message
#             console.alert(msg)
#             return None, None
#
#     @classmethod
#     def plugin(cls, plugin):
#         setattr(cls, plugin.func_name, plugin)