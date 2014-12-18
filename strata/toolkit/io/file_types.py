from mimetypes import MimeTypes


class FileType(object):
    __slots__ = ["name", "content_type", "binary"]
    __lookup__ = {}

    def __init__(self, name, content_type, binary=True):
        self.name = name
        self.content_type = content_type
        self.binary = binary

    @staticmethod
    def register(extension, content_type, binary=True):
        extension = extension.strip().lower()
        if extension.find(".") > -1:
            extension = extension[1:]

        tbl = FileType.__lookup__
        try:
            return tbl[extension]
        except:
            ft = FileType(extension, content_type, binary=binary)
            tbl[extension] = ft
            return ft

    @staticmethod
    def find(extension):
        extension = extension.strip().lower()
        if extension.find(".") > -1:
            extension = extension[1:]

        tbl = FileType.__lookup__
        try:
            return tbl[extension]
        except KeyError:
            try:
                mime_type = MimeTypes().guess_type("file.%s" % extension)
                if mime_type is not None and mime_type[0] is not None:
                    binary = True
                    content_type = mime_type[0]
                    if content_type.lower().find("text") > -1:
                        binary = False
                    return FileType.register(extension, content_type, binary=binary)

            except:
                return tbl["*"]


FileType.register("*",      "application/octet-stream", binary=True)
FileType.register("txt",    "text/plain", binary=False)
FileType.register("html",   "text/html", binary=False)
FileType.register("htm",    "text/html", binary=False)
FileType.register("xml",    "text/xml", binary=False)
FileType.register("js",     "application/x-javascript", binary=False)
FileType.register("css",    "text/css", binary=False)
FileType.register("json",   "application/json", binary=False)
FileType.register("sql",    "text/plain", binary=False)
FileType.register("csv",    "text/csv", binary=False)
FileType.register("rtf",    "application/rtf", binary=False)
FileType.register("ini",    "text/plain", binary=False)
FileType.register("inf",    "text/plain", binary=False)
FileType.register("info",   "text/plain", binary=False)
FileType.register("config", "text/plain", binary=False)
FileType.register("cfg",    "text/plain", binary=False)
FileType.register("yaml",   "text/plain", binary=False)
FileType.register("xhtml",  "text/html", binary=False)
FileType.register("xht",    "text/xml", binary=False)
FileType.register("xsl",    "text/csv", binary=False)
FileType.register("xslt",   "text/csv", binary=False)
FileType.register("pdf",    "application/pdf", binary=False)

FileType.register("jpg",    "image/jpeg")
FileType.register("jpeg",   "image/jpeg")
FileType.register("gif",    "image/gif")
FileType.register("png",    "image/png")
FileType.register("bmp",    "image/bmp")

FileType.register("gz",     "application/x-gzip")
FileType.register("tar",    "application/x-tar")
FileType.register("zip",    "application/zip")
