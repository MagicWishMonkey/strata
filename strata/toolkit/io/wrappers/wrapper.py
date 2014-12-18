from ..file import File


class FileWrap(File):
    def __init__(self, uri):
        File.__init__(self, uri)
        self.encoder = lambda o: o
        self.decoder = lambda o: o
        self.buffer = []

    def append(self, o):
        o = self.encoder(o)
        self.buffer.append(o)
        return self

    def read(self):
        data = File.read(self)
        data = self.decoder(data)
        if isinstance(data, list) is True:
            self.buffer = data
            return self
        self.buffer = [data]
        return self

    def save(self):
        data = self.stringify()
        File.write_data(self, data)
        return self

    def stringify(self):
        buffer = self.buffer
        data = "\n".join(buffer)
        self.buffer = []
        File.write_data(self, data)
        return self

    def reload(self):
        wrap = self.__class__(self.uri)
        wrap.read()
        return wrap

    @classmethod
    def open(cls, uri):
        wrap = cls(uri)
        wrap.read()
        return wrap
