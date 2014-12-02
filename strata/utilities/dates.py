import sys
import time
import datetime
from datetime import timedelta
import dateutil.parser
from collections import namedtuple


Delta = namedtuple("Delta", "delta seconds minutes hours days weeks")


def try_parse(txt):
    """Parse the date string"""
    try:
        return dateutil.parser.parse(txt)
    except:
        if txt is None:
            return None

        if isinstance(txt, basestring) is False:
            try:
                return dateutil.parser.parse(txt.strftime("%Y-%m-%d %H:%M:%S"))
            except:
                pass
        return txt

def parse(txt):
    """Parse the date string"""
    try:
        return dateutil.parser.parse(txt)
    except Exception, ex:
        if isinstance(txt, basestring) is False:
            return dateutil.parser.parse(txt.strftime("%Y-%m-%d %H:%M:%S"))
        raise ex

datetime.parse = parse


def now():
    """Returns a datetime instance representing the current time."""
    return datetime.datetime.now()


def timestamp():
    """Return a datetime instance representing the current date/time"""
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return dt

datetime.timestamp = timestamp


def ticks():
    """Return the number of ticks since the epoch."""
    return time.time()


def prettify(*args):
    """Return a shortened string representing the amount of time
    elapsed between the two timestamps."""
    t1, t2 = None, None
    if len(args) == 1:
        t1, t2 = datetime.datetime.now(), args[0]
        if isinstance(t2, basestring) is True:
            t2 = parse(t2)
    elif len(args) == 2:
        t1, t2 = args[0], args[1]
        if isinstance(t1, basestring) is True:
            t1 = parse(t1)
        if isinstance(t2, basestring) is True:
            t2 = parse(t2)
    else:
        raise Exception("Please specify either 1 or 2 datetime parameters!")

    d = delta(t1, t2)

    if d.weeks > 0:
        days = (d.days + (d.weeks * 7))
        if d.hours > 0:
            return "%sd %sh" % (str(days), str(d.hours))
        return "%sd" % str(days)
    if d.days > 7:
        return "%sd" % str(d.days)
    elif d.days > 0:
        return "%sd %sh" % (str(d.days), str(d.hours))
    elif d.hours > 0:
        return "%sh %sm" % (str(d.hours), str(d.minutes))
    elif d.minutes > 0:
        return "%sm %ss" % (str(d.minutes), str(d.seconds))
    return "%ss" % str(d.seconds)


def delta(*args):
    """Returns a Delta instance representing the time difference."""
    t1, t2 = None, None
    if len(args) == 1:
        t1, t2 = datetime.datetime.now(), args[0]
        if isinstance(t2, basestring) is True:
            t2 = dateutil.parser.parse(t2)
    elif len(args) == 2:
        t1, t2 = args[0], args[1]
        if isinstance(t1, basestring) is True:
            t1 = dateutil.parser.parse(t1)
        if isinstance(t2, basestring) is True:
            t2 = dateutil.parser.parse(t2)
    else:
        raise Exception("Please specify either 1 or 2 datetime parameters!")

    multiplier = 1
    if t1 > t2:
        t1, t2 = (t2, t1)
        multiplier = -1

    d = t2 - t1

    days, seconds = d.days, d.seconds
    minutes, hours, weeks, months = 0, 0, 0, 0
    offset = seconds
    if seconds > 0:
        minutes = (seconds / 60)
        seconds = (seconds - (minutes * 60))
        if minutes > 60:
            hours = (minutes / 60)
            minutes = (minutes - (hours * 60))

    if days > 0:
        offset = (seconds + (days * 86400))
        if days > 7:
            weeks = (days / 7)
            days = (days - (weeks * 7))

    if multiplier == -1:
        offset = (offset * -1)

    return Delta(offset, seconds, minutes, hours, days, weeks)


def difference(*args):
    """Returns the number of seconds between the two dates."""
    t1, t2 = None, None
    if len(args) == 1:
        t1, t2 = datetime.datetime.now(), args[0]
        if isinstance(t2, basestring) is True:
            t2 = dateutil.parser.parse(t2)
    elif len(args) == 2:
        t1, t2 = args[0], args[1]
        if isinstance(t1, basestring) is True:
            t1 = dateutil.parser.parse(t1)
        if isinstance(t2, basestring) is True:
            t2 = dateutil.parser.parse(t2)
    else:
        raise Exception("Please specify either 1 or 2 datetime parameters!")

    if t1 > t2:
        t1, t2 = t2, t1
    d = t2 - t1
    days = d.days
    seconds = d.seconds
    if days > 0:
        seconds = ((days * 86400) + seconds)
    return seconds



def offset(
        date=None,
        microseconds=0,
        seconds=0,
        minutes=0,
        hours=0,
        days=0,
        weeks=0,
        months=0):
    """Return a datetime instance with the specified offset."""
    if date is not None:
        if isinstance(date, basestring) is True:
            date = dateutil.parser.parse(date)
    else:
        date = datetime.datetime.now()
    try:
        if months != 0 and weeks == 0:
            weeks = months * 4
        subtract = False
        if microseconds < 0:
            subtract = True
            microseconds = microseconds * -1
        if seconds < 0:
            subtract = True
            seconds = seconds * -1
        if minutes < 0:
            subtract = True
            minutes = minutes * -1
        if hours < 0:
            subtract = True
            hours = hours * -1
        if days < 0:
            subtract = True
            days = days * -1
        if weeks < 0:
            subtract = True
            weeks = weeks * -1

        dt = date
        td = timedelta(
            microseconds=microseconds,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks
        )
        ndt = dt - td if subtract else dt + td
        return ndt
    except:
        if microseconds is None:
            microseconds = 0
        if seconds is None:
            seconds = 0
        if minutes is None:
            minutes = 0
        if hours is None:
            hours = 0
        if days is None:
            days = 0
        if weeks is None:
            weeks = 0
        if months is None:
            months = 0

        return offset(
            date=date,
            microseconds=microseconds,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            days=days,
            weeks=weeks,
            months=months
        )