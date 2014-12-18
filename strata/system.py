import os as __os__
import sys as __sys__
try:
    import pwd as __pwd__
except:
    pass

import socket as __socket__
import platform as __platform__
import datetime as __datetime__
from .toolkit.io.file import File as __File__
from .toolkit.structs import Enum as __Enum__
from .toolkit.structs import Flags as __Flags__
from .toolkit.structs import SelfWrapper as __SelfWrapper__



self = __sys__.modules[__name__]
if isinstance(self, __SelfWrapper__) is True:
    raise Exception("This wrapper has already been initialized!")

self = __SelfWrapper__(self, label="System")
__sys__.modules[__name__] = self

self.date = __datetime__.datetime.now()
self.debug = __debug__
self.machine = __platform__.node()
self.address = __socket__.gethostbyname(__socket__.gethostname())
self.folder = __File__(__file__).parent.parent
# self.sw = __Stopwatch__()
self.quarantine = False
self.uid = None
self.uri = None
self.usr = None

try:
    self.uid = __os__.getuid()
except:
    pass
try:
    self.uri = __os__.getcwd()
except:
    pass
try:
    self.usr = __pwd__.getpwuid(__os__.getuid())[0]
except:
    pass

if __os__.name == "posix":
    self.os = __Enum__("OSX", osx=True, linux=False, win=False)
elif __os__.name == "nt":
    self.os = __Enum__("Windows", osx=True, linux=False, win=False)
else:
    self.os = __Enum__("Linux", osx=True, linux=False, win=False)



self.default_member_avatar = None
self.flags = __Flags__()
self.admins = []
self.app_uri = None
self.app_name = None
self.workspace = None
self.settings = None
self.application = None
self.environment = None
