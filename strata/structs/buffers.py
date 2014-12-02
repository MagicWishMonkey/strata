

class RollingCache(object):
    def __init__(self, max_size=1000, decoder=None, encoder=None):
        self.max_size = max_size
        self.decoder = decoder
        self.encoder = encoder
        self.index = []
        self.lookup = {}
        self.counter = 0

    def clear(self):
        self.index = []
        self.lookup = {}
        self.counter = 0

    def contains(self, key):
        try:
            return True if self.lookup[key] else False
        except ValueError:
            return False

    def contains(self, key):
        if isinstance(key, basestring):
            key = key.__hash__()

        try:
            return True if self.lookup[key] else False
        except ValueError:
            return False

    def try_get(self, key):
        if isinstance(key, basestring):
            key = key.__hash__()

        try:
            return self.lookup[key]
        except ValueError:
            return None

    def get(self, key):
        if isinstance(key, basestring):
            key = key.__hash__()

        val = self.lookup.get(key, None)
        if val is None:
            return None

        fn = self.decoder
        if fn:
            val = fn(val)
        return val

    def set(self, key, obj):
        if isinstance(key, basestring):
            key = key.__hash__()

        val = obj
        cleanup = False
        fn = self.encoder
        if fn:
            val = fn(val)

        counter = self.counter
        tbl = self.lookup
        try:
            existing = tbl[key]
            tbl[key] = val
        except KeyError:
            tbl[key] = val
            self.index.append(key)
            counter += 1
            if (counter % 10) == 0:
                if counter >= self.max_size:
                    cleanup = True

        if cleanup is True:
            self.cleanup()

        return obj

    def cleanup(self):
        """Clean out the oldest cache entries."""
        indexes = self.index
        tbl = self.lookup
        cnt = len(indexes)
        threshold = (self.max_size - 100)

        x = 0
        while cnt > threshold:
            ix = indexes[x]
            indexes[x] = None
            tbl.pop(ix)
            x += 1
            cnt -= 1
        self.indexes = [ix for ix in indexes if ix]
        self.counter = 0

    @property
    def size(self):
        return len(self.index)

    def __repr__(self):
        return "RollingCache -> %d items" % len(self.indexes)

    def __str__(self):
        return self.__repr__()