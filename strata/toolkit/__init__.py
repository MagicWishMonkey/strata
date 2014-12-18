from .structs import *
from .person import Person
from .emails import EmailAddress
from .emails import DomainName
from .io import File, Directory
from .crypto import *
from ..threads import current_thread
from .. import types
import time
from datetime import datetime
import base64 as __b64__
try:
    import simplejson as __json__
except ImportError:
    print "Unable to import the simplejson library. Degrading to the built in json module."
    import json as __json__
import cStringIO
import cPickle
import gzip as __gzip__
import zlib as __zlib__
import uuid
import hashlib
import urllib
import urllib2


def file(uri):
    return File(uri)


def folder(uri):
    return Directory(uri)


def rcurry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(more_a + a), **dict(kw, **more_kw))
    return curried


def curry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(a + more_a), **dict(kw, **more_kw))
    return curried


def context():
    ctx = current_thread.get("context")
    if ctx is not None:
        return ctx

    from .. import system
    app = system.application
    if app is None:
        raise Exception("The application has not been initialized.")
    return app.context()
    # from fuze.context import Context
    # return Context.current()


def is_email(email):
    return EmailAddress.is_valid(email)


def format_email(email):
    return EmailAddress.format(email)


def unroll(o, omit_null=False):
    if not o:
        return []

    if isinstance(o, (list, tuple)) is False:
        return [o]

    def __append__(values, omit_null, o):
        for i in o:
            if isinstance(i, (list, tuple)) is True:
                __append__(values, omit_null, i)
                continue
            if omit_null is True and i is None:
                continue
            values.append(i)
        return values
    values = __append__([], omit_null, o)
    return values




def guid(*size):
    size = 32 if len(size) == 0 else size[0]
    if size is None or size < 1:
        size = 32

    txt = hashlib.md5(str(uuid.uuid4())).hexdigest()
    if size == 32:
        return txt
    if size < 32:
        return txt[0:size]

    while len(txt) < size:
        txt = "%s%s" % (txt, hashlib.md5(str(uuid.uuid4())).hexdigest())

    if len(txt) > size:
        txt = txt[0:size]
    return txt


def sleep(*seconds):
    """Puts the current thread to sleep for the specified number of seconds."""
    seconds = 0.01 if len(seconds) == 0 else seconds[0]
    time.sleep(seconds)


def hash(data):
    return hashlib.md5(data).hexdigest()



def stringify(o, pretty=False):
    """Convert the specified object to a string. If the input object
     is a list type convert each object in the list to a string and return."""
    if o is None:
        return ""
    elif isinstance(o, basestring):
        return o
    elif isinstance(o, datetime):
        return o.strftime("%Y-%m-%d %H:%M:%S")

    try:
        if is_model(o) is True:
            object = o.deflate()
            return json(object, indent=2) if pretty is True else json(object)

        if isinstance(o, list):
            if len(o) == 0:
                return "[]"
            if is_model(o[0]) is True:
                objects = [o.deflate() for o in o]
                return json(objects, indent=2) if pretty is True else json(objects)

            if isinstance(o[0], (int, basestring, long, float)) is True:
                if isinstance(o[0], int) is True:
                    try:
                        return ",".join([str(k) for k in o])
                    except:
                        return ",".join([str(k) for k in o if k is not None])
                if isinstance(o[0], basestring) is True:
                    return "\n".join(o)

                try:
                    try:
                        if pretty is True:
                            return "[%s]" % ",".join([str(k) for k in o])
                        return ",".join([str(k) for k in o])
                    except:
                        if pretty is True:
                            return "[%s]" % ",".join([str(k) for k in o if k is not None])
                        return ",".join([str(k) for k in o if k is not None])

                except:
                    if pretty is True:
                        return "[%s]" % ",".join([str(k) for k in o if k is not None])
                    return ",".join([str(k) for k in o if k is not None])

            if pretty is True:
                return json(o, indent=3)
            return json(o)




        if isinstance(o, dict):
            if pretty is True:
                return json(o, indent=3)
            return json(o)
        elif hasattr(o, "__dict__"):
            if pretty is True:
                return json(o.__dict__, indent=3)
            return json(o.__dict__)

        return str(o)
    except Exception, ex:
        raise Exception(
            "Unable to stringify the object! %s" % ex.message
        )




def web_get(uri, *headers):
    header_table = {}
    if len(headers) > 0:
        for header in headers:
            key, val = None, None
            if isinstance(header, basestring) is True:
                parts = header.split(":") if header.find(":") > -1 else header.split("=")
                if len(parts) < 2:
                    raise Exception("The header format is not valid.")
                key = parts[0].strip()
                val = ":".join(parts[1:]).strip() if header.find(":") > -1 else "=".join(parts[1:]).strip()
            else:
                if isinstance(header, (tuple, list)) is False:
                    raise Exception("The header format is not valid.")
                key, val = header[0], header[1]
            header_table[key] = val
    #header_table['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/530.33 (KHTML, like Gecko) Chrome/1.2.3.4 Safari/555.44'

    headers = []
    for key in header_table:
        val = header_table[key]
        headers.append((key, val))

    opener = urllib2.build_opener()
    opener.addheaders = headers
    response = opener.open(uri)
    data = response.read()
    return data


def web_post(uri, data, *headers):
    header_table = {}
    if len(headers) > 0:
        for header in headers:
            key, val = None, None
            if isinstance(header, basestring) is True:
                parts = header.split(":") if header.find(":") > -1 else header.split("=")
                if len(parts) < 2:
                    raise Exception("The header format is not valid.")
                key = parts[0].strip()
                val = ":".join(parts[1:]).strip() if header.find(":") > -1 else "=".join(parts[1:]).strip()
            else:
                if isinstance(header, (tuple, list)) is False:
                    raise Exception("The header format is not valid.")
                key, val = header[0], header[1]
            header_table[key] = val

    #header_table['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/530.33 (KHTML, like Gecko) Chrome/1.2.3.4 Safari/555.44'

    if isinstance(data, (list, dict)) is True:
        data = json(data)
        header_table["Content-Type"] = "application/json"
    header_table["Content-Length"] = str(len(data))

    req = urllib2.Request(uri, data, headers=header_table)
    response = urllib2.urlopen(req)
    result = response.read()
    return result


def encode_url_params(**kwd):
    buffer = []
    for key in kwd:
        val = kwd[key]
        if val is None:
            buffer.append("{key}=".format(key=key))
            continue

        if val is not None:
            try:
                val = urllib.quote(val)
            except:
                val = urllib.quote(str(val))
        buffer.append("{key}={val}".format(key=key, val=val))
    params = "&".join(buffer)
    return params


def sql_sanitize(sql):
    """Sanitize the sql statement, replace naughty characters and whatnot."""
    print "TODO: implement the sql sanitize function"
    return sql


def base64(data):
    """Convert the string to base64."""
    data = __b64__.encodestring(data)
    while data.find("\n") > -1:
        data = data.replace("\n", "")
    #data = data.replace("\n", "")
    return data


def unbase64(data):
    """Convert the string from base64."""
    data = __b64__.decodestring(data)
    return data


def base36(num):
    """Convert the object instance into Base36."""
    assert num is not None, "The input parameter is null!"
    assert isinstance(num, (int, long)), "The input parameter must be an integer!"
    assert num > -1, "The input parameter must be a positive integer."

    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    try:
        txt = ""
        while num:
            num, i = divmod(num, 36)
            txt = chars[i] + txt
        return txt or chars[0]

    except Exception, ex:
        message = "Unable to encode the data to base64-> %s" % ex.message
        raise Exception(message)

def unbase36(data):
    """Convert the data from Base36."""
    assert data is not None, "The input parameter is null!"
    try:
        return int(data, 36)
    except Exception, ex:
        message = "Unable to decode the base36 data-> %s" % ex.message
        raise Exception(message)

def json_nice(obj):
    return json(obj, indent=2)

def json(obj, indent=None, sort_keys=True, pretty=False):
    """Convert the object instance into a json blob."""
    assert obj is not None, "The input parameter is null!"

    try:
        if indent:
            return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=indent)
        else:
            if pretty is True:
                return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=2)
            return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys)
    except Exception, ex:
        message = "Unable to encode the object to json-> %s" % ex.message
        raise Exception(message)



def unjson(data, silent=False):
    """Convert the json blob into an object instance."""
    assert data is not None, "The input parameter is null!"

    if silent is True:
        try:
            txt = data.strip()
            pfx, sfx = txt[0], txt[len(txt) - 1]
            if pfx == "[" and sfx == "]" or pfx == "{" and sfx == "}":
                try:
                    return __json__.loads(data, strict=False)
                except:
                    return None
            return None
        except:
            return None

    try:
        return __json__.loads(data, strict=False)
    except Exception, ex:
        message = "Unable to decode the json object-> %s" % ex.message
        raise Exception(message)


def pickle(obj, protocol=2):
    """Pickles the object instance"""
    assert obj is not None, "The obj parameter is null!"

    try:
        return cPickle.dumps(obj, protocol)
    except Exception, ex:
        message = "Unable to pickle the object instance-> %s" % ex.message
        raise Exception(message)


def unpickle(data):
    """Unpickles the object instance"""
    assert data is not None, "The data parameter is null!"

    try:
        return cPickle.loads(data)
    except Exception, ex:
        message = "Unable to unpickle the object instance-> %s" % ex.message
        raise Exception(message)


def gzip(data, compression_level=9):
    assert data is not None, "The data parameter is null!"

    buffer = cStringIO.StringIO()
    try:
        file = __gzip__.GzipFile(mode='wb',  fileobj=buffer, compresslevel=compression_level)
        file.write(data)
        file.close()

        data = buffer.getvalue()
        return data
    except Exception, ex:
        message = "Unable to gzip compress the data-> %s" % ex.message
        raise Exception(message)
    finally:
        buffer.close()


def ungzip(data, compression_level=9):
    assert data is not None, "The data parameter is null!"

    buffer = cStringIO.StringIO(data)
    try:
        file = __gzip__.GzipFile(mode='rb',  fileobj=buffer, compresslevel=compression_level)
        data = file.read()
        file.close()
        buffer.close()
        return data
    except Exception, ex:
        message = "Unable to gzip decompress the data-> %s" % ex.message
        raise Exception(message)
    finally:
        buffer.close()

def zlib(data):
    assert data is not None, "The data parameter is null!"
    return __zlib__.compress(data)


def unzlib(data):
    assert data is not None, "The data parameter is null!"
    return __zlib__.decompress(data)


def compress(data):
    assert data is not None, "The data parameter is null!"
    return __zlib__.compress(data)


def decompress(data):
    assert data is not None, "The data parameter is null!"
    return __zlib__.decompress(data)



def serialize(*models):
    if len(models) == 0:
        return None

    single = False
    if len(models) == 1:
        if isinstance(models[0], list) is False:
            single = True

    models = unroll(models)
    if len(models) == 0:
        return []
    docs = [m.serialize() for m in models]
    if single is True:
        return None if len(docs) == 0 else docs[0]
    return docs


def deserialize(data):
    obj = unjson(data)
    single = False
    if isinstance(obj, list) is False:
        single = True
        obj = [obj]

    for x, o in enumerate(obj):
        uri = o["_"]
        type = uri.split("#")[0]
        cls = types.MetaModel.find(type)
        model = cls(**(o))
        obj[x] = model

    if single is True:
        return obj[0] if len(obj) > 0 else None
    return obj


################################################################
## TYPE CHECKING
################################################################
is_string = types.is_string
not_string = types.not_string
is_list = types.is_list
not_list = types.not_list
is_num = types.is_num
not_num = types.not_num
is_blank = types.is_blank
not_blank = types.not_blank
is_function = types.is_function
is_class = types.is_class
not_class = types.not_class
is_model = types.is_model
parse_bool = types.parse_bool
parse_int = types.parse_int
