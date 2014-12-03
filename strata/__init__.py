#from fuze.errors import *
from strata.utilities import *
from strata.structs import *
from strata.io import *
from strata import system
from strata import util
from strata import toolkit
from strata import types
from strata import system
from strata.log import Logger
from strata.app import App
import atexit


app = App.get()
logger = Logger.get()
trace = lambda *message: Logger.get().trace(*message)
debug = lambda *message: Logger.get().debug(*message)


# terminal = log.terminal()
# trace = lambda *message: terminal.blue(*message)

is_win = lambda: system.os.win
is_osx = lambda: system.os.osx

empty = lambda o: True if not o else False
is_str = lambda o: isinstance(o, basestring)
is_num = lambda o: isinstance(o, (int, long))
is_int = lambda o: isinstance(o, int)
is_list = lambda o: isinstance(o, (list, tuple))
is_dict = lambda o: isinstance(o, dict)


#atexit.register(App.destroy)


# # Python 3 compatibility hack
# if sys.version_info[:2] >= (3, 0):
#     # pylint: disable=E0611,F0401
#     import pickle
#     from urllib.request import build_opener
#     from urllib.error import HTTPError, URLError
#     py2utf8_encode = lambda x: x
#     py2utf8_decode = lambda x: x
#     compat_input = input
# else:
#     from urllib2 import build_opener, HTTPError, URLError
#     import cPickle as pickle
#     py2utf8_encode = lambda x: x.encode("utf8")
#     py2utf8_decode = lambda x: x.decode("utf8")
#     compat_input = raw_input