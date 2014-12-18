import socket
import platform
from .toolkit import *





REVISION=1.15 #2014-08-12 17:34:42
QUARANTINE = False
OVERRIDE_MAIL_RECIPIENT = None
DISABLE_EMAIL = False
START_TIME = None
LOCAL_MODE = False
ADMINISTRATORS = []
CONFIG = None

ENVIRONMENT = Enum("Production", debug=False)
RELEASE_MODE = False
ADMIN_MODE = False
LOG_LEVEL = 1

parts = __file__.split("/")
parts.pop()
CODE_PATH = "/".join(parts)
#print CODE_PATH

parts.pop()
HOME_PATH = "/".join(parts)

LOGGER = None
WORKSPACE = None


PROJECT = "topferral"
APP_URI = "http://localhost/"
APP_SHARE_URI = "http://localhost/"
MACHINE = platform.node()
IP_ADDRESS = None

try:
    IP_ADDRESS = socket.gethostbyname(socket.gethostname())
except:
    print "Unable to get the local ip address"

EXCHANGE_ENDPOINT = None

EMAIL_RECIPIENT_WHITELIST = [
    "rodenberg@gmail.com",
    "@whoat.net",
    "@sharkblazers.com",
    "@guerrillamail.com",
    "@guerrillamail.net",
    "@guerrillamail.org",
    "@guerrillamail.biz",
    "@guerrillamailblock.com",
    "@sharklasers.com",
    "@ronweb.net"
]
ENABLE_SPOOLING = True
HOLIDAYS = {}

DEFAULT_CONTACT_AVATAR_THUMB_URI = "https://s3.amazonaws.com/whoat_assets/images/member_avatar.png"

DEFAULT_MEMBER_AVATAR_THUMB_URI = "https://s3.amazonaws.com/whoat_assets/images/member_avatar.png"
DEFAULT_MEMBER_AVATAR_MED_URI = "https://s3.amazonaws.com/whoat_assets/images/member_avatar_med.png"
DEFAULT_MEMBER_AVATAR_BIG_URI = "https://s3.amazonaws.com/whoat_assets/images/member_avatar_big.png"

DEFAULT_COMPANY_AVATAR_THUMB_URI = "https://s3.amazonaws.com/whoat_assets/images/member_avatar.png"

DEFAULT_GROUP_INVITE_SUBJECT = "Group invitation"
DEFAULT_GROUP_INVITE_MESSAGE = "Will you join my group?"

SMS_ALERT_FLAG = False

LETTERS = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
NUMBERS = ["0","1","2","3","4","5","6","7","8","9"]



class Environments(object):
    Development = Enum("Development")
    Alpha = Enum("Alpha")
    Beta = Enum("Beta")
    Production = Enum("Production")


class Weekdays(object):
    Monday      = Enum("Monday",    code=0, weekday=True,  holiday=False, date=0)
    Tuesday     = Enum("Tuesday",   code=1, weekday=True,  holiday=False, date=0)
    Wednesday   = Enum("Wednesday", code=2, weekday=True,  holiday=False, date=0)
    Thursday    = Enum("Thursday",  code=3, weekday=True,  holiday=False, date=0)
    Friday      = Enum("Friday",    code=4, weekday=True,  holiday=False, date=0)
    Saturday    = Enum("Saturday",  code=5, weekday=False, holiday=False, date=0)
    Sunday      = Enum("Sunday",    code=6, weekday=False, holiday=False, date=0)


class Months(object):
    January = Enum("January",      code=1)
    February = Enum("February",     code=2)
    March = Enum("March",        code=3)
    April = Enum("April",        code=4)
    May = Enum("May",          code=5)
    June = Enum("June",         code=6)
    July = Enum("July",         code=7)
    August = Enum("August",       code=8)
    September = Enum("September",    code=9)
    October = Enum("October",      code=10)
    November = Enum("November",     code=11)
    December = Enum("December",     code=12)
