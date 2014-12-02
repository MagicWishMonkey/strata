import os as __os__
import sys as __sys__
try:
    import pwd as __pwd__
except:
    pass

import socket as __socket__
import platform as __platform__
import datetime as __datetime__
from strata.structs.containers import Wrapper as __Wrapper__
from strata.structs.containers import SelfWrapper as __SelfWrapper__
from strata.structs.containers import Flags as __Flags__
from strata.structs.person import Person as __Person__
from strata.structs.enums import Enum as __Enum__
from strata.io.file import File as __File__
from strata.utilities.stopwatch import Stopwatch as __Stopwatch__
from strata.utilities.reflection import Reflector as __Reflector__




def __uptime__(self):
    sw = self.sw
    return sw.milliseconds


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
self.sw = __Stopwatch__()
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


self.log = None
try:
    from strata.log import Logger as __Logger__
    self.log = __Logger__.get()
except:
    pass


# self.app = None
# try:
#     from fuze.app import App as __App__
#     self.app = __App__.get()
# except:
#     pass

self.flags = __Flags__()
self.admins = []
self.app_data = None
self.settings = None
self.application = None
self.environment = None
try:
    from strata import util as __util__
    self.app_data = self.folder.reverse_search("@app_data")
    settings = self.app_data.file("settings.json")
    settings = settings.read(__util__.unjson)
    settings = __util__.wrap(settings)

    settings_override = self.app_data.file("settings.override.json")
    settings_override = settings_override.read(__util__.unjson)
    settings_override = __util__.wrap(settings_override)
    settings.override(settings_override)
    self.flags.bind(**(settings.flags))
    if self.flags.quarantine is True:
        self.quarantine = True

    if settings.application.quarantine is True:
        self.quarantine = True

    self.settings = settings
    self.application = settings.application.name
    self.environment = settings.application.environment

    admins = settings.application.administrators
    if admins:
        if isinstance(admins, list) is False:
            admins = [admins]
        for admin in admins:
            person = __Person__.parse(admin)
            if person is not None:
                if person.email is not None:
                    if person.email.valid is True:
                        self.admins.append(person)
except Exception, ex:
    message = "Error initializing settings: %s" % ex.message
    print message

self.uptime = __Reflector__.curry(__uptime__, self)

self.seal()