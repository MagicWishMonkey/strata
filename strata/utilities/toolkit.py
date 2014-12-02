# import base64 as __b64__
# try:
#     import simplejson as __json__
# except ImportError:
#     print "Unable to import the simplejson library. Degrading to the built in json module."
#     import json as __json__
# import cStringIO
# import cPickle
# import gzip as __gzip__
# import zlib as __zlib__
# import uuid
# import hashlib
# from fuze.utilities.logger import Logger as __logger__
#
# log = __logger__.get()
#
#
# def rcurry(f, *a, **kw):
#     def curried(*more_a, **more_kw):
#         return f(*(more_a + a), **dict(kw, **more_kw))
#     return curried
#
#
# def curry(f, *a, **kw):
#     def curried(*more_a, **more_kw):
#         return f(*(a + more_a), **dict(kw, **more_kw))
#     return curried
#
#
# def guid(*size):
#     size = 32 if len(size) == 0 else size[0]
#     if size is None or size < 1:
#         size = 32
#
#     txt = hashlib.md5(str(uuid.uuid4())).hexdigest()
#     if size == 32:
#         return txt
#     if size < 32:
#         return txt[0:size]
#
#     while len(txt) < size:
#         txt = "%s%s" % (txt, hashlib.md5(str(uuid.uuid4())).hexdigest())
#
#     if len(txt) > size:
#         txt = txt[0:size]
#     return txt
#
# def hash(data):
#     return hashlib.md5(data).hexdigest()
#
#
# def base64(data):
#     """Convert the string to base64."""
#     data = __b64__.encodestring(data)
#     while data.find("\n") > -1:
#         data = data.replace("\n", "")
#     #data = data.replace("\n", "")
#     return data
#
#
# def unbase64(data):
#     """Convert the string from base64."""
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
#     chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     try:
#         txt = ""
#         while num:
#             num, i = divmod(num, 36)
#             txt = chars[i] + txt
#         return txt or chars[0]
#
#     except Exception, ex:
#         message = "Unable to encode the data to base64-> %s" % ex.message
#         raise Exception(message)
#
# def unbase36(data):
#     """Convert the data from Base36."""
#     assert data is not None, "The input parameter is null!"
#     try:
#         return int(data, 36)
#     except Exception, ex:
#         message = "Unable to decode the base36 data-> %s" % ex.message
#         raise Exception(message)
#
# def json_nice(obj):
#     return json(obj, indent=2)
#
# def json(obj, indent=None, sort_keys=True, pretty=False):
#     """Convert the object instance into a json blob."""
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
#         raise Exception(message)
#
#
#
# def unjson(data, silent=False):
#     """Convert the json blob into an object instance."""
#     assert data is not None, "The input parameter is null!"
#
#     if silent is True:
#         try:
#             txt = data.strip()
#             pfx, sfx = txt[0], txt[len(txt) - 1]
#             if pfx == "[" and sfx == "]" or pfx == "{" and sfx == "}":
#                 try:
#                     return __json__.loads(data, strict=False)
#                 except:
#                     return None
#             return None
#         except:
#             return None
#
#     try:
#         return __json__.loads(data, strict=False)
#     except Exception, ex:
#         message = "Unable to decode the json object-> %s" % ex.message
#         raise Exception(message)
#
#
# def pickle(obj, protocol=2):
#     """Pickles the object instance"""
#     assert obj is not None, "The obj parameter is null!"
#
#     try:
#         return cPickle.dumps(obj, protocol)
#     except Exception, ex:
#         message = "Unable to pickle the object instance-> %s" % ex.message
#         raise Exception(message)
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
#         raise Exception(message)
#
#
# def gzip(data, compression_level=9):
#     assert data is not None, "The data parameter is null!"
#
#     buffer = cStringIO.StringIO()
#     try:
#         file = __gzip__.GzipFile(mode='wb',  fileobj=buffer, compresslevel=compression_level)
#         file.write(data)
#         file.close()
#
#         data = buffer.getvalue()
#         return data
#     except Exception, ex:
#         message = "Unable to gzip compress the data-> %s" % ex.message
#         raise Exception(message)
#     finally:
#         buffer.close()
#
#
# def ungzip(data, compression_level=9):
#     assert data is not None, "The data parameter is null!"
#
#     buffer = cStringIO.StringIO(data)
#     try:
#         file = __gzip__.GzipFile(mode='rb',  fileobj=buffer, compresslevel=compression_level)
#         data = file.read()
#         file.close()
#         buffer.close()
#         return data
#     except Exception, ex:
#         message = "Unable to gzip decompress the data-> %s" % ex.message
#         raise Exception(message)
#     finally:
#         buffer.close()
#
# def zlib(data):
#     assert data is not None, "The data parameter is null!"
#     return __zlib__.compress(data)
#
#
# def unzlib(data):
#     assert data is not None, "The data parameter is null!"
#     return __zlib__.decompress(data)
#
#
# def compress(data):
#     assert data is not None, "The data parameter is null!"
#     return __zlib__.compress(data)
#
#
# def decompress(data):
#     assert data is not None, "The data parameter is null!"
#     return __zlib__.decompress(data)
#
#
