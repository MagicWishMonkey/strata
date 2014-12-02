import urllib2 as __urlib2__


class Uri(object):
    __slots__ = ["__uri__", "__parts__", "__params__"]

    def __init__(self, *uri):
        self.__uri__ = None if len(uri) == 0 else uri[0]
        self.__params__ = None
        self.__parts__ = (None, None, None)
        self.__fix__()

    def __fix__(self):
        uri = self.__uri__
        if uri is None:
            self.__params__ = None
            self.__parts__ = (None, None, None)
            return

        if uri.lower().startswith("www.") is True:
            uri = "http://%s" % uri
        else:
            if uri.lower().startswith("http://") is False:
                if uri.lower().startswith("https://") is False:
                    uri = "http://%s" % uri

        self.__uri__ = uri
        ix = uri.find("://")
        uri = uri[ix+3:]
        parts = uri.split("?")
        query_string = None
        if len(parts) > 1:
            uri = parts[0]
            #self.__uri__ = uri
            query_string = "?".join(parts[1:])

        domain, path, port = None, None, None

        parts = uri.split("/")
        domain = parts[0]
        path = "/".join(parts[1:]) if len(parts) > 1 else ""
        if path:
            path = self.unquote(path)
        if domain.find(":") > -1:
            inner = domain.split(":")
            domain = inner[0]
            if inner[1].isdigit() and inner[1] != "80":
                port = int(inner[1])

        params = None
        self.__parts__ = (domain, path, port)
        if query_string is not None:
            params = []
            parts = query_string.split("&")
            for part in parts:
                inner = part.split("=")
                key, val = inner[0], None
                if len(inner) > 1:
                    if len(inner) == 2:
                        val = inner[1]
                    else:
                        val = "=".join(inner[1:])
                    val = self.unquote(val)
                params.append((key, val))
        self.__params__ = params

    def add_param(self, key, val):
        params = self.__params__
        key = key.strip()
        if params is None:
            params = []
        else:
            for x, o in enumerate(params):
                k = o[0]
                if k.lower() == key.lower():
                    params[x] = (key, val)
                    return self
        if isinstance(val, basestring) is False:
            if val is None:
                val = ""
            else:
                val = str(val)
        params.append((key, val))
        return self

    def get_param(self, key):
        params = self.__params__
        key = key.strip()
        if params is None:
            return None

        for x, o in enumerate(params):
            k = o[0]
            if k.lower() == key.lower():
                return o[1]
        return None

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
    def query_string(self):
        params = self.__params__
        if not params:
            return ""

        buffer = []
        for key, val in params:
            if val:
                val = self.quote(val)
            buffer.append("%s=%s" % (key, val))
        query_string = "&".join(buffer)
        return query_string

    @property
    def domain(self):
        return self.__parts__[0]

    @property
    def path(self):
        path = self.__parts__[1]
        return path

    @property
    def port(self):
        return self.__parts__[2]

    @property
    def name(self):
        path = self.__parts__[1]
        if not path:
            return path
        parts = path.split("/")
        name = parts[len(parts) - 1]
        return name

    @property
    def uri(self):
        uri = self.__uri__
        if uri is None:
            return None

        query_string = self.query_string
        if query_string:
            uri = "%s?%s" % (uri, query_string)
        return uri

    @uri.setter
    def uri(self, uri):
        self.__uri__ = None if not uri else uri
        self.__fix__()

    @classmethod
    def create(cls, *uri):
        return cls(*uri)

    def __str__(self):
        return self.uri

    def __repr__(self):
        return self.uri
