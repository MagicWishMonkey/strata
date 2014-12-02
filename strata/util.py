import time
# import cStringIO
import urllib2
import uuid
from strata import toolkit
# from fuze import const
from .utilities import *
from .http import *
from .threads import *
from .io import *
from .crypto import *
from .errors import *
from strata import types
from strata.utilities.emails import EmailAddress, DomainName


def reflector():
    return Reflector()


def uri_unquote(txt):
    return urllib2.unquote(txt)


def web_get(uri, *headers):
    if len(headers) > 0:
        headers = list(headers)

    headers = list(headers) if len(headers) > 0 else []
    headers.append(('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/530.33 (KHTML, like Gecko) Chrome/1.2.3.4 Safari/555.44'))

    opener = urllib2.build_opener()
    opener.addheaders = headers
    response = opener.open(uri)
    data = response.read()
    return data


def request(uri, **headers):
    request = Request(uri, **headers)
    return request



# def download(uri, file):
#     headers = {}
#     headers["User-Agent"] = "Mozilla/5.0 Chrome/34.1.2222.1111 Safari/511.56"
#     headers["Accept-Encoding"] = "gzip,deflate,compress"
#     headers["Accept-Language"] = "en-US,en;q=0.8"
#     headers["Referer"] = "https://www.google.com/"
#     headers["Accept"] = "*/*"
#     request = requests.get(uri, headers=headers, timeout=120, stream=True)
#
#     if isinstance(file, basestring) is True:
#         file = File(file)
#
#     temp = file.parent.file("%s.temp" % file.uri)
#     try:
#         flush_bytes = 0
#         with open(temp.uri, 'wb') as f:
#             for chunk in request.iter_content(chunk_size=10240):
#                 if chunk is not None: # filter out keep-alive new chunks
#                     f.write(chunk)
#             #         flush_bytes = (flush_bytes + (len(chunk) * 1024))
#             #         if flush_bytes > 1024:
#             #             f.flush()
#             #             flush_bytes = 0
#             # if flush_bytes > 0:
#             #     util.trace("Flushing {count} bytes...".format(count=flush_bytes))
#             #     f.flush()
#     except Exception, ex:
#         message = "Error downloading the file: %s" % ex.message
#         print message
#
#
#     incomplete, retries = True, 0
#     while incomplete is True and retries < 5:
#         if retries > 0:
#             io.delete(temp)
#             util.sleep(5)
#
#         r = requests.get(uri, headers=headers, timeout=120, stream=True)
#         try:
#             flush_bytes = 0
#             with open(temp, 'wb') as f:
#                 for chunk in r.iter_content(chunk_size=10240):
#                     if chunk is not None: # filter out keep-alive new chunks
#                         f.write(chunk)
#                         flush_bytes = (flush_bytes + (len(chunk) * 1024))
#                         if flush_bytes > 1024:
#                             f.flush()
#                             flush_bytes = 0
#
#                 if flush_bytes > 0:
#                     util.trace("Flushing {count} bytes...".format(count=flush_bytes))
#                     f.flush()
#
#
#             io.move(temp, path)
#             file["size"] = io.file_size(path)
#             incomplete = False
#         except Exception, ex:
#             message = "Error downloading the file '{name}' -> {message}".format(name=name, message=ex.message)
#             util.trace(message)
#             retries = (retries + 1)

# def fetch_file_size(uri):
#     try:
#         request = requests.head(uri)
#         headers = request.headers
#         for header in headers:
#             if header.lower() == "content-length":
#                 bytes = headers[header]
#                 if isinstance(bytes, basestring) is True:
#                     bytes = int(bytes)
#
#                 kb = 1 if bytes < 1024 else round((float(bytes) / float(1024)), 2)
#                 return kb
#                 # if kb < 1024:
#                 #     return kb
#                 # mb = round((float(kb) / float(1024)), 2)
#                 # return mb
#         return 0
#     except:
#         return 0




def guid(*size):
    size = 32 if len(size) == 0 else size[0]
    txt = hashlib.md5(str(uuid.uuid4())).hexdigest()
    cnt = len(txt)

    while size > cnt:
        txt = "%s%s" % (txt, hashlib.md5(str(uuid.uuid4())).hexdigest())
        cnt = len(txt)

    if cnt > size:
        txt = txt[0:size]

    return txt



def dispatch(fn, *args, **kwd):
    if len(args) > 0 or len(kwd) > 0:
        fn = curry(fn, *args, **kwd)
    return Worker.launch(fn)


def dedupe(lst):
    tbl, filtered = {}, False
    for x, o in enumerate(lst):
        try:
            if tbl[o] is not None:
                filtered = True
                lst[x] = None
        except KeyError:
            tbl[o] = 1

    if filtered is True:
        lst = [o for o in lst if o is not None]
    return lst



def stripper(txt, pattern):
    if pattern == basestring:
        buffer = [c for c in txt if c.isdigit() is False]
        return "".join(buffer)
    elif pattern == int or pattern == float:
        digits = digitize(txt)
        if digits is None:
            return 0 if pattern == int else 0.0
    print "ADD ABILITY TO STRIP OTHER TYPES!"
    return txt


def dedigitize(txt):
    buffer = [c for c in txt if c.isdigit() is False]
    return "".join(buffer)


def digitize(txt):
    buffer = []
    integer = True
    for c in txt:
        if c.isdigit() is True:
            buffer.append(c)
            continue

        if integer is False or len(buffer) == 0:
            continue

        if c == ".":
            integer = False
            buffer.append(c)

    if len(buffer) == 0:
        return None

    txt = "".join(buffer)
    if integer is False:
        return float(txt)
    return int(txt)




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


# def hash(data):
#     return md5(data)
#
#
# def base64(data):
#     data = __b64__.encodestring(data)
#     while data.find("\n") > -1:
#         data = data.replace("\n", "")
#     #data = data.replace("\n", "")
#     return data
#
#
# def unbase64(data):
#     data = __b64__.decodestring(data)
#     return data
#
#
# def base36(num):
#     """Convert the object instance into Base36."""
#     assert num is not None, "The input parameter is null!"
#     assert isinstance(num, (int, long)), "The input parameter must be an integer!"
#     assert num > -1, "The input parameter must be a positive integer."
#
#     chars = const.BASE_36_CHARS
#     try:
#         txt = ""
#         while num:
#             num, i = divmod(num, 36)
#             txt = chars[i] + txt
#         return txt or chars[0]
#
#     except Exception, ex:
#         message = "Unable to encode the data to base64-> %s" % ex.message
#         raise FuzeError(message, ex)
#
#
# def unbase36(data):
#     """Convert the data from Base36."""
#     assert data is not None, "The input parameter is null!"
#     try:
#         return int(data, 36)
#     except Exception, ex:
#         message = "Unable to decode the base36 data-> %s" % ex.message
#         raise FuzeError(message, ex)
#
#
# def json(obj, indent=None, sort_keys=True, pretty=False):
#     """Convert the object instance into a json blob."""
#
#     assert obj is not None, "The input parameter is null!"
#
#     try:
#         if indent:
#             return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=indent)
#         else:
#             if pretty is True:
#                 return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys, indent=2)
#             return __json__.dumps(obj, check_circular=False, sort_keys=sort_keys)
#     except Exception, ex:
#         message = "Unable to encode the object to json-> %s" % ex.message
#         raise FuzeError(message, ex)
#
#
#
# def unjson(data):
#     """Convert the json blob into an object instance."""
#     assert data is not None, "The input parameter is null!"
#
#     try:
#         return __json__.loads(data, strict=False)
#     except Exception, ex:
#         message = "Unable to decode the json object-> %s" % ex.message
#         raise FuzeError(message, ex)


# def pickle(obj, protocol=2):
#     """Pickles the object instance"""
#     assert obj is not None, "The obj parameter is null!"
#
#     try:
#         return cPickle.dumps(obj, protocol)
#     except Exception, ex:
#         message = "Unable to pickle the object instance-> %s" % ex.message
#         raise FuzeError(message, ex)
#
#
# def unpickle(data):
#     """Unpickles the object instance"""
#     assert data is not None, "The data parameter is null!"
#
#     try:
#         return cPickle.loads(data)
#     except Exception, ex:
#         message = "Unable to unpickle the object instance-> %s" % ex.message
#         raise FuzeError(message, ex)


def file(uri):
    return File(uri)


def directory(uri):
    return Directory(uri)


def folder(uri):
    return Directory(uri)


def trace(o):
    print o
    return str(o)


def rcurry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(more_a + a), **dict(kw, **more_kw))
    return curried


def curry(f, *a, **kw):
    def curried(*more_a, **more_kw):
        return f(*(a + more_a), **dict(kw, **more_kw))
    return curried


def wrap(*args, **kw):
    return Wrapper.create(*args, **kw)


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


# def unroll(lst):
#     if lst is None:
#         return []
#     def list_or_tuple(x):
#         return isinstance(x, (list, tuple))
#
#     def flatten(seq, to_expand=list_or_tuple):
#         for i in seq:
#             if to_expand(i):
#                 for sub in flatten(i, to_expand):
#                     yield sub
#             else:
#                 yield i
#
#     if list_or_tuple(lst) is False:
#         return [lst]
#
#     unravelled = []
#     for o in flatten(lst):
#         unravelled.append(o)
#     return unravelled


def empty(o):
    if not o:
        return True
    return False


def numeric(txt):
    buffer = []
    integer = True
    for c in txt:
        if c.isdigit() is True:
            buffer.append(c)
            continue

        if integer is False or len(buffer) == 0:
            continue

        if c == ".":
            integer = False
            buffer.append(c)

    if len(buffer) == 0:
        return None

    txt = "".join(buffer)
    if integer is False:
        return float(txt)
    return int(txt)


def sleep(*seconds):
    """Puts the current thread to sleep for the specified number of seconds."""
    seconds = 0.01 if len(seconds) == 0 else seconds[0]
    time.sleep(seconds)


def stopwatch():
    return Stopwatch()


def chunk(lst, cnt):
    """break the input array into a list of smaller arrays of the specified size"""
    buffers = []
    buffer = []
    for o in lst:
        buffer.append(o)
        if len(buffer) == cnt:
            buffers.append(buffer)
            buffer = []

    if len(buffer) > 0:
        buffers.append(buffer)

    return buffers
    #return [lst[k:k+cnt] for k in xrange(0, len(lst), cnt)]


def chunks(lst, cnt, *filter):
    """break the input array into a list of smaller arrays of the specified size"""
    filter = None if len(filter) == 0 else filter[0]
    buffer = []
    for o in lst:
        if filter is not None:
            o = filter(o)
            if o is None:
                continue

        buffer.append(o)
        if len(buffer) == cnt:
            cpy = buffer
            buffer = []
            yield cpy
    if len(buffer) > 0:
        yield buffer


def context():
    from strata.context import Context
    return Context.current()


def is_email(email):
    return EmailAddress.is_valid(email)


def format_email(email):
    return EmailAddress.format(email)

# def gzcompress(data, compression_level=9):
#     assert data is not None, "The data parameter is null!"
#
#     buffer = cStringIO.StringIO()
#     try:
#         file = gzip.GzipFile(mode='wb',  fileobj=buffer, compresslevel=compression_level)
#         file.write(data)
#         file.close()
#
#         data = buffer.getvalue()
#         return data
#     except Exception, ex:
#         message = "Unable to gzip compress the data-> %s" % ex.message
#         raise FuzeError(message, ex)
#     finally:
#         buffer.close()
#
#
# def gzdecompress(data, compression_level=9):
#     assert data is not None, "The data parameter is null!"
#
#     buffer = cStringIO.StringIO(data)
#     try:
#         file = gzip.GzipFile(mode='rb',  fileobj=buffer, compresslevel=compression_level)
#         data = file.read()
#         file.close()
#         buffer.close()
#         return data
#     except Exception, ex:
#         message = "Unable to gzip decompress the data-> %s" % ex.message
#         raise FuzeError(message, ex)
#     finally:
#         buffer.close()
#
#
# def compress(data):
#     assert data is not None, "The data parameter is null!"
#     return zlib.compress(data)
#
#
# def decompress(data):
#     assert data is not None, "The data parameter is null!"
#     return zlib.decompress(data)


json = toolkit.json
unjson = toolkit.unjson
hash = toolkit.hash
base64 = toolkit.base64
unbase64 = toolkit.unbase64
base36 = toolkit.base36
unbase36 = toolkit.unbase36
pickle = toolkit.pickle
unpickle = toolkit.unpickle
gzip = toolkit.gzip
ungzip = toolkit.ungzip
zlib = toolkit.zlib
unzlib = toolkit.unzlib
compress = toolkit.compress
decompress = toolkit.decompress
trace = toolkit.log.trace




def deflate(data):
    if isinstance(data, (list, dict)) is True:
        data = json(data)

    return base64(compress(data))


def inflate(data):
    o = decompress(unbase64(data))
    if o[0] == "{" or o[0] == "[":
        try:
            return unjson(o)
        except:
            return o
    return o




def sql_sanitize(sql):
    """Sanitize the sql statement, replace naughty characters and whatnot."""
    print "TODO: implement the sql sanitize function"
    return sql



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

