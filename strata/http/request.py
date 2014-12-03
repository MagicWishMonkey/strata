from strata.utilities import toolkit
from strata.http.uri import Uri
import urllib2 as __urlib2__
import requests


class Request(object):
    __slots__ = [
        "__uri__",
        "__headers__",
        "__method__",
        "__body__",
        "__form__",
        "__attrs__"
    ]

    def __init__(self, uri, **headers):
        self.__uri__ = Uri.create(uri)
        self.__method__ = "GET"
        self.__headers__ = None
        self.__body__ = None
        self.__form__ = None
        self.__attrs__ = None
        for name in headers:
            value = headers[name]
            self.add_header(name, value)

    def attach(self, *data, **form):
        if len(form) > 0:
            for name in form:
                value = form[name]
                self.add_param(name, value)
            return self

        if len(data) > 0:
            data = data[0]
            self.body = data

        return self

    @property
    def attributes(self):
        attributes = self.__attrs__
        if attributes is None:
            attributes = {}
            self.__attrs__ = attributes
        return attributes

    @property
    def uri(self):
        return self.__uri__.uri

    @property
    def method(self):
        return self.__method__

    @method.setter
    def method(self, method):
        method = method.strip().lower()
        if method == "get":
            self.__method__ = "GET"
        elif method == "post":
            self.__method__ = "POST"
        elif method == "head":
            self.__method__ = "HEAD"
        elif method == "delete":
            self.__method__ = "DELETE"
        else:
            raise Exception("The specified method is not supported: %s" % method.upper())

    @property
    def form(self):
        form = self.__form__
        if form is None:
            return None

        buffer = []
        for x, o in enumerate(form):
            key, val = o[0], o[1]
            if val:
                val = self.quote(val)
            buffer.append("%s=%s" % (key, val))

        form = "&".join(buffer)
        return form

    @property
    def body(self):
        body = self.__body__
        if body is not None:
            return body
        return self.form

    @body.setter
    def body(self, val):
        if not val:
            self.__body__ = None
            return
        if isinstance(val, (list, dict)) is True:
            val = toolkit.json(val)
            self.add_header("Content-Type", "application/json")
        self.__body__ = val

    @property
    def headers(self):
        headers = self.__headers__
        if not headers:
            return []

        buffer = []
        for key, val in headers:
            buffer.append("%s=%s" % (key, val))
        return buffer

    def header(self, name, *value):
        if len(value) == 0:
            self.get_header(name)
        else:
            value = value[0]
            self.add_header(name, value)
        return self

    def param(self, name, *value):
        if len(value) == 0:
            self.get_param(name)
        else:
            value = value[0]
            self.add_param(name, value)
        return self

    def add_header(self, key, val):
        headers = self.__headers__
        key = key.strip()
        if headers is None:
            headers = []
            self.__headers__ = headers
        else:
            for x, o in enumerate(headers):
                k = o[0]
                if k.lower() == key.lower():
                    headers[x] = (key, str(val))
                    return self
        if isinstance(val, basestring) is False:
            if val is None:
                val = ""
            else:
                val = str(val)
        headers.append((key, val))
        return self

    def get_header(self, key):
        headers = self.__headers__
        key = key.strip()
        if headers is None:
            return None

        for x, o in enumerate(headers):
            k = o[0]
            if k.lower() == key.lower():
                return o[1]
        return None

    def add_param(self, key, val):
        form = self.__form__
        key = key.strip()
        if isinstance(val, (dict, list)) is True:
            val = toolkit.json(val)

        if form is None:
            form = []
            self.__form__ = form
        else:
            for x, o in enumerate(form):
                k = o[0]
                if k.lower() == key.lower():
                    form[x] = (key, val)
                    return self
        if isinstance(val, basestring) is False:
            if val is None:
                val = ""
            else:
                val = str(val)
        form.append((key, val))
        return self

    def get_param(self, key):
        form = self.__form__
        if form is None:
            return None

        key = key.strip()
        for x, o in enumerate(form):
            k = o[0]
            if k.lower() == key.lower():
                return o[1]
        return None

    def get_attr(self, key):
        key = key.strip().lower()
        try:
            return self.attributes[key]
        except KeyError:
            return None

    def set_attr(self, key, val):
        key = key.strip().lower()
        self.attributes[key] = val

    def quote(self, *args):
        if len(args) == 0:
            return ""
        if len(args) == 1:
            return __urlib2__.quote(args[0])
        lst = []
        for arg in args:
            if arg is None:
                lst.append("")
                continue
            lst.append(__urlib2__.quote(arg))
        return lst

    def unquote(self, *args):
        if len(args) == 0:
            return ""
        if len(args) == 1:
            return __urlib2__.unquote(args[0])
        lst = []
        for arg in args:
            if arg is None:
                lst.append("")
                continue
            lst.append(__urlib2__.unquote(arg))
        return lst

    @property
    def size(self):
        size = self.get_attr("size")
        if size is not None:
            return size
        uri = self.uri
        try:
            request = requests.head(uri)
            headers = request.headers
            for header in headers:
                if header.lower() == "content-length":
                    bytes = headers[header]
                    if isinstance(bytes, basestring) is True:
                        bytes = int(bytes)

                    kb = 1 if bytes < 1024 else round((float(bytes) / float(1024)), 2)
                    self.set_attr("size", kb)
                    return kb
            self.set_attr("size", 0)
            return 0
        except:
            return 0

    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)

    @classmethod
    def create(cls, uri, **headers):
        return cls(uri, **headers)

    def __str__(self):
        return "HttpRequest: %s" % self.uri

    def __repr__(self):
        return self.__str__()


@Request.plugin
def HEAD(self, ignore_errors=False, formatter=None):
    uri = self.uri
    toolkit.log.trace("HTTP %s: %s" % ("HEAD", uri))

    response_content = None
    try:
        response = requests.head(uri)
        if response.content is not None:
            response_content = response.content
        else:
            response_content = response.text
    except Exception, ex:
        if ignore_errors is True:
            return None
        message = "Error with HTTP HEAD request: %s > %s" % (uri, ex.message)
        if response_content is not None:
            message = "%s\n%s" % (message, response_content)
        raise Exception(message)

    if formatter is not None:
        content = formatter(response_content)
    if content is not None:
        return content
    return response_content


@Request.plugin
def GET(self, ignore_errors=False, formatter=None):
    self.method = "GET"
    return self.execute(ignore_errors=ignore_errors, formatter=formatter)


@Request.plugin
def POST(self, ignore_errors=False, formatter=None):
    self.method = "POST"
    return self.execute(ignore_errors=ignore_errors, formatter=formatter)


@Request.plugin
def execute(self, ignore_errors=False, formatter=None):
    method = self.method
    if method == "HEAD":
        return self.HEAD(ignore_errors=ignore_errors, formatter=formatter)

    uri = self.uri
    request = None
    if method == "GET":
        request = requests.get
    elif method == "POST":
        request = requests.post
    else:
        raise Exception("The http method is not currently supported: %s" % method)

    data = self.body
    if data is not None:
        self.add_header("content-length", len(data))

    headers = self.headers
    if headers is not None:
        headers = dict((h[0], h[1]) for h in headers)

    if headers is None:
        request = toolkit.curry(request, uri)
    else:
        request = toolkit.curry(request, uri, headers=headers)

    toolkit.log.trace("HTTP %s: %s" % (method, uri))

    response = None
    try:
        response = request()
    except Exception, ex:
        message = "Error with the HTTP GET request-> %s\n%s" % (uri, ex.message)
        raise Exception(message)

    response_content = None
    if response.content is not None:
        response_content = response.content
    else:
        response_content = response.text

    content = toolkit.unjson(response_content, silent=True)
    if content is not None:
        response_content = content

    status_code = response.status_code
    if status_code == 404 or status_code == 500 and ignore_errors is False:
        if isinstance(response_content, (list, dict)) is True:
            response_content = toolkit.json_nice(response_content)
        if response_content is None:
            response_content = ""
        message = "[%s] ERROR > %s " % (str(status_code), response_content)
        raise Exception(message)

    if formatter is not None:
        content = formatter(response_content)
        if content is not None:
            return content
    return response_content


@Request.plugin
def download(self, file, async=False, callback=None, block_size=1024):
    try:
        from strata import util
    except:
        message = "Unable to import the fuze util module."
        raise Exception(message)

    if isinstance(file, basestring) is False:
        try:
            file = file.uri
        except Exception, ex:
            message = "Invalid file parameter! %s" % ex.message
            raise Exception(message)


    def __stream__(uri, file, flush_limit=1024, callback=None):
        if flush_limit is None or flush_limit < 1:
            flush_limit = 1024

        headers = {}
        headers["User-Agent"] = "Mozilla/5.0 Chrome/34.1.2222.1111 Safari/511.56"
        headers["Accept-Encoding"] = "gzip,deflate,compress"
        headers["Accept-Language"] = "en-US,en;q=0.8"
        headers["Referer"] = "https://www.google.com/"
        headers["Accept"] = "*/*"
        request = requests.get(uri, headers=headers, timeout=120, stream=True)

        try:
            bytes_total = 0
            flush_count = 0
            with open(file, 'wb') as f:
                for chunk in request.iter_content(chunk_size=10240):
                    if chunk is not None: # filter out keep-alive new chunks
                        f.write(chunk)
                        cnt = (len(chunk) * 1024)
                        bytes_total = (bytes_total + cnt)
                        flush_count = (flush_count + cnt)
                        if flush_count > flush_limit:
                            flush_count = 0
                            f.flush()
        except Exception, ex:
            message = "Error downloading the file: %s" % ex.message
            print message
            raise Exception(message)

        if callback is not None:
            callback()

    uri = self.uri
    fn = util.curry(__stream__, uri, file, flush_limit=block_size, callback=callback)
    if async is True:
        util.dispatch(fn)
        return self

    fn()
    return self


# def GET(self, *fmt):
#     self.method = "GET"
#     data = self.body
#     if data and self.has_header("Content-length") is False:
#         self.header("Content-length", len(data))
#
#     uri = self.to_uri()
#     #print uri
#     #logger.info("http.GET %s" % uri)
#     headers = self.headers
#     try:
#         if headers and data:
#             response = requests.get(uri, data=data, headers=headers)
#         elif data:
#             response = requests.get(uri, data=data)
#         elif headers:
#             response = requests.get(uri, headers=headers)
#         else:
#             response = requests.get(uri)
#
#         status_code = response.status_code
#         if status_code == 404 or status_code == 500:
#             try:
#                 from fusion import tools
#                 if response.content is not None:
#                     response = response.content
#                 else:
#                     response = response.text
#
#                 return tools.unjson(response)
#             except:
#                 pass
#             reason = response.reason
#             raise HttpRequestException("[%s] Http request failed: %s" % (str(status_code), reason))
#
#         if response.content is not None:
#             response = response.content
#         else:
#             response = response.text
#         if len(fmt) > 0:
#             fmt = fmt[0]
#             response = fmt(response)
#         return response
#     except Exception, ex:
#         if isinstance(ex, HttpRequestException) is True:
#             raise ex
#
#         raise HttpRequestException(
#             "Error with the HTTP GET request-> %s\n%s" % (uri, ex.message), ex
#         )
#
# def HEAD(self):
#     self.method = "HEAD"
#     uri = self.to_uri()
#     headers = self.headers
#     try:
#         response = requests.head(uri)
#         if response.content is not None:
#             response = response.content
#         else:
#             response = response.text
#         return response
#     except Exception, ex:
#         raise HttpRequestException(
#             "Error with the HTTP HEAD request-> %s\n%s" % (uri, ex.message), ex
#         )
# class Request(object):
#     def __init__(self, uri, *headers):
#         self.__uri = uri
#         self.__headers = {}
#         self.__params = None
#         self.__locals = None
#         self.__method = "GET"
#
#         if len(headers) > 0:
#             header_table = self.__headers
#             for header in headers:
#                 key, val = None, None
#                 if isinstance(header, basestring) is True:
#                     parts = header.split(":") if header.find(":") > -1 else header.split("=")
#                     if len(parts) < 2:
#                         raise Exception("The header format is not valid.")
#                     key = parts[0].strip()
#                     val = ":".join(parts[1:]).strip() if header.find(":") > -1 else "=".join(parts[1:]).strip()
#                 else:
#                     if isinstance(header, (tuple, list)) is False:
#                         raise Exception("The header format is not valid.")
#                     key, val = header[0], header[1]
#                 header_table[key.lower()] = val
#
#     def set_local(self, key, val):
#         tbl = self.__locals
#         if tbl is None:
#             self.__locals = {}
#             tbl = self.__locals
#         tbl[key] = val
#
#     def get_local(self, key, default=None):
#         tbl = self.__locals
#         if tbl is None:
#             return None
#         try:
#             return tbl[key]
#         except KeyError:
#             return default
#
#
#
#     @property
#     def headers(self):
#         return self.__headers
#
#     @property
#     def uri(self):
#         uri = self.__uri
#         querystring = self.querystring
#         if not querystring:
#             return uri
#
#         uri = "%s?%s" % (uri, querystring)
#         return uri
#
#     @property
#     def method(self):
#         return self.__method
#
#     @method.setter
#     def method(self, method):
#         method = method.strip().lower()
#         if method == "get":
#             self.__method = "GET"
#         elif method == "post":
#             self.__method = "POST"
#         elif method == "head":
#             self.__method = "HEAD"
#         elif method == "delete":
#             self.__method = "DELETE"
#         else:
#             raise Exception("The specified method is not supported: %s" % method.upper())
#
#     def set_header(self, key, val):
#         headers = self.__headers
#         if key.lower() == "content-length":
#             key = key.lower()
#
#         if isinstance(val, basestring) is False:
#             val = str(val)
#
#         headers[key] = val
#         return self
#
#     def get_header(self, key):
#         headers = self.__headers
#         try:
#             return headers[key.strip().lower()]
#         except KeyError:
#             return None
#
#     # def has_header(self, key):
#     #     return True if self.get_header(key) else False
#     #
#     # def as_post(self):
#     #     self.__method = "POST"
#     #     return self
#     #
#     # def as_get(self):
#     #     self.__method = "GET"
#     #     return self
#
#     @classmethod
#     def plugin(cls, plugin):
#         name = plugin.func_name
#         setattr(cls, name, plugin)
#
#     @property
#     def query_string(self):
#         return self.__uri__.query_string
#
#     @property
#     def size(self):
#         uri = self.uri
#         try:
#             request = requests.head(uri)
#             headers = request.headers
#             for header in headers:
#                 if header.lower() == "content-length":
#                     bytes = headers[header]
#                     if isinstance(bytes, basestring) is True:
#                         bytes = int(bytes)
#
#                     kb = 1 if bytes < 1024 else round((float(bytes) / float(1024)), 2)
#                     self.set_local("size", kb)
#                     return kb
#             return 0
#         except:
#             return 0
#
#     def __str__(self):
#         return self.uri
#
#     def __repr__(self):
#         return self.__str__()
#
#
#     # def POST(self):
#     #     self._method = "POST"
#     #     data = self.body
#     #     if data is None:
#     #         if self._form:
#     #             data = urllib.urlencode(self._form)
#     #             #data = "&".join(self._form)
#     #             if self.content_type is None:
#     #                 self.content_type = "application/x-www-form-urlencoded"
#     #     if self.has_header("Content-Length") is False:
#     #         if data:
#     #             self.header("Content-Length", len(data))#(len(data) * 8))
#     #         else:
#     #             self.header("Content-Length", 0)
#     #             #if data and self.has_header("Content-length") is False:
#     #             #    self.header("Content-length", len(data))
#     #
#     #     if self.content_type is not None:
#     #         self.header("Content-Type", self.content_type)
#     #
#     #     #print data
#     #     uri = self.to_uri()
#     #     #print uri
#     #     headers = self.headers
#     #     try:
#     #         if headers and data:
#     #             response = requests.post(uri, data=data, headers=headers, allow_redirects=True)
#     #         elif data:
#     #             response = requests.post(uri, data=data)
#     #         elif headers:
#     #             response = requests.post(uri, headers=headers)
#     #         else:
#     #             response = requests.post(uri)
#     #
#     #         status_code = response.status_code
#     #         if status_code == 404 or status_code == 500:
#     #             try:
#     #                 from fusion import tools
#     #                 if response.content is not None:
#     #                     response = response.content
#     #                 else:
#     #                     response = response.text
#     #
#     #                 return tools.unjson(response)
#     #             except:
#     #                 pass
#     #
#     #             reason = response.reason
#     #             raise HttpRequestException("[%s] Http request failed: %s" % (str(status_code), reason))
#     #
#     #         if response.content is not None:
#     #             response = response.content
#     #         else:
#     #             response = response.text
#     #
#     #         if self.callback is not None:
#     #             self.callback()
#     #         return response
#     #     except Exception, ex:
#     #         if isinstance(ex, HttpRequestException) is True:
#     #             raise ex
#     #
#     #         raise HttpRequestException(
#     #             "Error with the HTTP POST request-> %s\n%s" % (uri, ex.message), ex
#     #         )
#     #
#     # def GET(self, *fmt):
#     #     self.method = "GET"
#     #     data = self.body
#     #     if data and self.has_header("Content-length") is False:
#     #         self.header("Content-length", len(data))
#     #
#     #     uri = self.to_uri()
#     #     #print uri
#     #     #logger.info("http.GET %s" % uri)
#     #     headers = self.headers
#     #     try:
#     #         if headers and data:
#     #             response = requests.get(uri, data=data, headers=headers)
#     #         elif data:
#     #             response = requests.get(uri, data=data)
#     #         elif headers:
#     #             response = requests.get(uri, headers=headers)
#     #         else:
#     #             response = requests.get(uri)
#     #
#     #         status_code = response.status_code
#     #         if status_code == 404 or status_code == 500:
#     #             try:
#     #                 from fusion import tools
#     #                 if response.content is not None:
#     #                     response = response.content
#     #                 else:
#     #                     response = response.text
#     #
#     #                 return tools.unjson(response)
#     #             except:
#     #                 pass
#     #             reason = response.reason
#     #             raise HttpRequestException("[%s] Http request failed: %s" % (str(status_code), reason))
#     #
#     #         if response.content is not None:
#     #             response = response.content
#     #         else:
#     #             response = response.text
#     #         if len(fmt) > 0:
#     #             fmt = fmt[0]
#     #             response = fmt(response)
#     #         return response
#     #     except Exception, ex:
#     #         if isinstance(ex, HttpRequestException) is True:
#     #             raise ex
#     #
#     #         raise HttpRequestException(
#     #             "Error with the HTTP GET request-> %s\n%s" % (uri, ex.message), ex
#     #         )
#
#
#
#     # @property
#     # def querystring(self):
#     #     params = self.__params
#     #     if not params:
#     #         return ""
#     #
#     #     buffer = []
#     #     for key in params:
#     #         val = params[key]
#     #         if val is None:
#     #             val = ""
#     #         else:
#     #             val = urllib.urlencode(str(val))
#     #         buffer.append("%s=%s" % (key, val))
#     #
#     #     txt = "&".join(buffer)
#     #     return txt
#
#     @classmethod
#     def plugin(cls, plugin):
#         name = plugin.func_name
#         setattr(cls, name, plugin)
#
#     @property
#     def query_string(self):
#         return self.__uri__.query_string
#
#     @property
#     def size(self):
#         size = self.get_local("size")
#         if size is not None:
#             return size
#
#         uri = self.__uri
#         try:
#             request = requests.head(uri)
#             headers = request.headers
#             for header in headers:
#                 if header.lower() == "content-length":
#                     bytes = headers[header]
#                     if isinstance(bytes, basestring) is True:
#                         bytes = int(bytes)
#
#                     kb = 1 if bytes < 1024 else round((float(bytes) / float(1024)), 2)
#                     self.set_local("size", kb)
#                     return kb
#             return 0
#         except:
#             return 0
#
#     def __str__(self):
#         return self.uri
#
#     def __repr__(self):
#         return self.__str__()
#
# @Request.plugin
# def download(self, file, async=False, callback=None, block_size=1024):
#     try:
#         from fuze import util
#     except:
#         message = "Unable to import the fuze util module."
#         raise Exception(message)
#
#     if isinstance(file, basestring) is False:
#         try:
#             file = file.uri
#         except Exception, ex:
#             message = "Invalid file parameter! %s" % ex.message
#             raise Exception(message)
#
#
#     def __stream__(uri, file, flush_limit=1024, callback=None):
#         if flush_limit is None or flush_limit < 1:
#             flush_limit = 1024
#
#         headers = {}
#         headers["User-Agent"] = "Mozilla/5.0 Chrome/34.1.2222.1111 Safari/511.56"
#         headers["Accept-Encoding"] = "gzip,deflate,compress"
#         headers["Accept-Language"] = "en-US,en;q=0.8"
#         headers["Referer"] = "https://www.google.com/"
#         headers["Accept"] = "*/*"
#         request = requests.get(uri, headers=headers, timeout=120, stream=True)
#
#         try:
#             bytes_total = 0
#             flush_count = 0
#             with open(file, 'wb') as f:
#                 for chunk in request.iter_content(chunk_size=10240):
#                     if chunk is not None: # filter out keep-alive new chunks
#                         f.write(chunk)
#                         cnt = (len(chunk) * 1024)
#                         bytes_total = (bytes_total + cnt)
#                         flush_count = (flush_count + cnt)
#                         if flush_count > flush_limit:
#                             flush_count = 0
#                             f.flush()
#         except Exception, ex:
#             message = "Error downloading the file: %s" % ex.message
#             print message
#             raise Exception(message)
#
#         if callback is not None:
#             callback()
#
#     uri = self.uri
#     fn = util.curry(__stream__, uri, file, flush_limit=block_size, callback=callback)
#     if async is True:
#         util.dispatch(fn)
#         return self
#
#     fn()
#     return self
#
#
#
#
# # def download(uri, file):
# #     headers = {}
# #     headers["User-Agent"] = "Mozilla/5.0 Chrome/34.1.2222.1111 Safari/511.56"
# #     headers["Accept-Encoding"] = "gzip,deflate,compress"
# #     headers["Accept-Language"] = "en-US,en;q=0.8"
# #     headers["Referer"] = "https://www.google.com/"
# #     headers["Accept"] = "*/*"
# #     request = requests.get(uri, headers=headers, timeout=120, stream=True)
# #
# #     if isinstance(file, basestring) is True:
# #         file = File(file)
# #
# #     temp = file.parent.file("%s.temp" % file.uri)
# #     try:
# #         flush_bytes = 0
# #         with open(temp.uri, 'wb') as f:
# #             for chunk in request.iter_content(chunk_size=10240):
# #                 if chunk is not None: # filter out keep-alive new chunks
# #                     f.write(chunk)
# #                     #         flush_bytes = (flush_bytes + (len(chunk) * 1024))
# #                     #         if flush_bytes > 1024:
# #                     #             f.flush()
# #                     #             flush_bytes = 0
# #                     # if flush_bytes > 0:
# #                     #     util.trace("Flushing {count} bytes...".format(count=flush_bytes))
# #                     #     f.flush()
# #     except Exception, ex:
# #         message = "Error downloading the file: %s" % ex.message
# #         print message
# #
# #
# #     incomplete, retries = True, 0
# #     while incomplete is True and retries < 5:
# #         if retries > 0:
# #             io.delete(temp)
# #             util.sleep(5)
# #
# #         r = requests.get(uri, headers=headers, timeout=120, stream=True)
# #         try:
# #             flush_bytes = 0
# #             with open(temp, 'wb') as f:
# #                 for chunk in r.iter_content(chunk_size=10240):
# #                     if chunk is not None: # filter out keep-alive new chunks
# #                         f.write(chunk)
# #                         flush_bytes = (flush_bytes + (len(chunk) * 1024))
# #                         if flush_bytes > 1024:
# #                             f.flush()
# #                             flush_bytes = 0
# #
# #                 if flush_bytes > 0:
# #                     util.trace("Flushing {count} bytes...".format(count=flush_bytes))
# #                     f.flush()
# #
# #
# #             io.move(temp, path)
# #             file["size"] = io.file_size(path)
# #             incomplete = False
# #         except Exception, ex:
# #             message = "Error downloading the file '{name}' -> {message}".format(name=name, message=ex.message)
# #             util.trace(message)
# #             retries = (retries + 1)
#
