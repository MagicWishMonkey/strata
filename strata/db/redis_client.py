from strata import *
from strata.db.config import Config
from redis import Redis



class RedisClient(object):
    __buckets__ = {}

    __slots__ = [
        "config",
        #"__buckets__",
        "__connect__",
        "__server__"
    ]

    def __init__(self, config, connect=None):
        self.config = config
        if connect is None:
            cfg = {
                "host": config.uri,
                "port": config.port
            }
            if config.username is not None:
                cfg["username"] = config.username
            if config.password is not None:
                cfg["password"] = config.password

            connect = util.curry(Redis, **(cfg))
        self.__connect__ = connect
        #self.__buckets__ = RedisClient.__buckets__
        self.__server__ = None

    def ping(self):
        try:
            self.server.ping()
            return True
        except Exception, ex:
            message = "The redis server is offline. %s" % ex.message
            print message
            return False


    @property
    def server(self):
        server = self.__server__
        if server is None:
            server = self.__connect__()
            self.__server__ = server
        return server

    @property
    def label(self):
        return self.config.label

    def clone(self):
        return RedisClient(
            self.config,
            connect=self.__connect__
        )

    def get(self, bucket):
        key = bucket.strip().lower()
        tbl = RedisClient.__buckets__
        try:
            return tbl[key].clone(self)
        except:
            return None

    def bucket(self, name, ttl=None, encoder=None, decoder=None, adapter=None, keygen=None):
        key = name.strip().lower()
        tbl = RedisClient.__buckets__
        try:
            return tbl[key].clone(self)
        except:
            bucket = Bucket(
                None,
                name,
                ttl=ttl,
                encoder=encoder,
                decoder=decoder,
                adapter=adapter,
                keygen=keygen
            )
            tbl[key] = bucket
            return bucket.clone(self)

    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)

    def rpush(self, name, *values):
        server = self.server
        with server.pipeline() as pipeline:
            for value in values:
                pipeline.rpush(name, value)

            pipeline.execute()

    def lpop(self, name):
        server = self.server
        o = server.lpop(name)
        return o

    def blpop(self, name, *timeout):
        timeout = 0 if len(timeout) == 0 else timeout[0]
        server = self.server
        o = server.blpop(name, timeout)
        return o

    def pipeline(self, ttl=None):
        return Pipeline(self, ttl=ttl)

    def queue(self, label):
        return RedisQueue(self, label)

    @classmethod
    def open(cls, **kwd):
        driver = kwd.get("driver", None)
        if driver is None:
            raise Exception("The database driver is not specified.")

        params = kwd.get("params", {})
        config = Config(
            driver=driver,
            label=kwd.get("label", None),
            uri=kwd.get("uri", None),
            database=kwd.get("database", None),
            username=kwd.get("username", None),
            password=kwd.get("password", None),
            port=kwd.get("port", None),
            params=params
        )
        return cls(config)

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.__repr__()



class RedisQueue(object):
    def __init__(self, server, label):
        self.__server__ = server
        self.__label__ = label

    @property
    def label(self):
        return self.__label__

    @property
    def db(self):
        return self.__server__.server

    def pipeline(self):
        return self.__server__.pipeline()

    def push(self, *values):
        name = self.__label__
        with self.pipeline() as pipeline:
            for value in values:
                pipeline.pipeline.rpush(name, value)

    def get(self):
        return self.pop()

    def pop(self, timeout=None):
        try:
            if timeout is None or timeout < 1:
                return self.db.lpop(self.__label__)
            return self.db.blpop(self.__label__, timeout)
        except:
            return None

    def process(self, fn):
        while True:
            o = self.pop()
            if o is None:
                return
            fn(o)

    def clear(self):
        self.db.delete(self.__label__)
        return self.pop()


class Bucket(object):
    def __init__(self, server, name, **kwd):
        self.server = server
        self.name = name
        self.ttl = kwd.get("ttl", None)
        self.encoder = kwd.get("encoder", None)
        self.decoder = kwd.get("decoder", None)
        self.adapter = kwd.get("adapter", None)
        self.keygen = kwd.get("keygen", None)

    def clone(self, server):
        return Bucket(
            server,
            self.name,
            ttl=self.ttl,
            encoder=self.encoder,
            decoder=self.decoder,
            adapter=self.adapter,
            keygen=self.keygen
        )

    def encode(self, *objects):
        encoder = self.encoder
        keygen = self.keygen
        if keygen is None:
            # keygen = lambda o: str(o)
            self.keygen = keygen
            if len(objects) > 0:
                if util.is_model(objects[0]):
                    keygen = objects[0].repository_class.keygen
                    self.keygen = keygen
            if keygen is None:
                keygen = lambda o: str(o)

        if encoder is None:
            for object in objects:
                key = keygen(object)
                yield key, object

        for object in objects:
            data = encoder(object)
            key = keygen(object)
            yield key, data

    def pipeline(self):
        return self.server.pipeline(ttl=self.ttl)

    def save(self, *objects):
        objects = util.unroll(objects)
        cnt = len(objects)
        if cnt == 0:
            return
        if cnt == 1 and isinstance(objects[0], list) is True:
            objects = objects[0]
        with self.pipeline() as pipeline:
            for key, val in self.encode(*(objects)):
                pipeline.set(key, val)

    def get(self, key):
        return self.fetch(key)

    def fetch(self, *keys):
        if len(keys) == 0:
            return None

        single = False
        if len(keys) == 1:
            if isinstance(keys[0], list) is False:
                single = True

        keys = util.unroll(keys)
        if len(keys) == 1 and isinstance(keys[0], list) is True:
            keys = keys[0]
        if isinstance(keys[0], basestring) is True:
            if keys[0].isdigit() is True:
                keys = map(int, keys)

        if isinstance(keys[0], int) is True:
            keygen = self.keygen
            keys = map(keygen, keys)

        objects = []
        decoder = self.decoder
        with self.pipeline() as pipeline:
            for key in keys:
                object = pipeline.get(key, decoder=decoder)
                if object is not None:
                    objects.append(object)

        if single is True:
            if len(objects) == 0:
                return None
            return objects[0]
        return objects

    def delete(self, *keys):
        if len(keys) == 0:
            return None

        keys = util.unroll(keys)
        if isinstance(keys[0], basestring) is True:
            if keys[0].isdigit() is True:
                keys = map(int, keys)

        if isinstance(keys[0], int) is True:
            keygen = self.keygen
            keys = map(keygen, keys)

        with self.pipeline() as pipeline:
            for key in keys:
                pipeline.delete(key)

class Pipeline(object):
    __slots__ = ["__server__", "__pipeline__", "__ttl__"]
    def __init__(self, server, ttl=None):
        self.__server__ = server
        self.__ttl__ = ttl
        self.__pipeline__ = None

    @property
    def db(self):
        return self.__server__.server

    @property
    def pipeline(self):
        pipeline = self.__pipeline__
        if pipeline is None:
            pipeline = self.__server__.server.pipeline()
            self.__pipeline__ = pipeline
        return pipeline

    def __enter__(self):
        self.__pipeline__ = self.__server__.server.pipeline()
        return self

    def __exit__(self, error_type, error_val, error_tb):
        self.__server__ = None
        pipeline = self.__pipeline__

        if error_val is not None:
            type = error_type.__name__
            message = error_val.message
            raise Exception(message)

        if pipeline is not None:
            try:
                pipeline.execute()
            except Exception, ex:
                message = "Error executing pipeline: %s" % ex.message
                print message

            self.__pipeline__ = None

    def delete(self, key):
        pipeline = self.pipeline
        self.__command__(pipeline.delete, key)

    def set(self, key, val):
        pipeline = self.pipeline
        ttl = self.__ttl__
        self.__command__(pipeline.set, key, val)
        if ttl is not None:
            self.__command__(pipeline.expire, key, ttl)

    def get(self, key, decoder=None):
        val = self.__command__(self.db.get, key)
        if val is not None and decoder is not None:
            val = decoder(val)
        return val


    def __command__(self, fn, key, *val):
        try:
            if len(val) == 0:
                o = fn(key)
                return o
            o = fn(key, val[0])
            #o = fn(key, val) if len(val) > 0 else fn(key)
            return o
        except Exception, ex:
            if self.__server__.ping() is True:
                message = "Error with redis: %s" % ex.message
                raise Exception(message)
            return None

# from fuze import util
# #from fuze import stats
# from fuze import log
# from fuze.errors import *
# from fuze.db.database import Database
# from redis import Redis
#
#
# class RedisServer(Database):
#     __slots__ = [
#         "config",
#         "server",
#         "buckets",
#         "queues",
#         "offline"
#     ]
#
#     def __init__(self, **config):
#         host = config.get("host", config.get("server", config.get("uri", None)))
#         port = config.get("port", 6379)
#         if isinstance(port, basestring) is True:
#             port = int(port)
#
#         username, password = config.get("username", None), config.get("password", None)
#
#         config = {
#             "host": host,
#             "port": port
#         }
#         if username is not None:
#             config["username"] = username
#         if password is not None:
#             config["password"] = password
#         self.config = config
#         self.server = Redis(**(config))
#         self.buckets = {}
#         self.queues = {}
#         self.offline = False
#         self.ping()
#
#     def ping(self):
#         def toggle(self, flag):
#             self.offline = flag
#             buckets = self.buckets.values()
#             for bucket in buckets:
#                 bucket.offline = flag
#
#         offline = self.offline
#         try:
#             self.engine.ping()
#             if offline == True:
#                 toggle(self, False)
#             return True
#         except Exception, ex:
#             log.error(FuzeError("Error pinging the database: %s" % ex.message, ex))
#             if offline == False:
#                 toggle(self, True)
#             return False
#
#     def bucket(self, name, encoder=None, decoder=None, ttl=None):
#         id = name.strip().lower()
#         try:
#             return self.buckets[id]
#         except KeyError:
#             bucket = Bucket(self, name, encoder=encoder, decoder=decoder, ttl=ttl)
#             self.buckets[id] = bucket
#             return bucket
#
#
# class Shard(object):
#     def __init__(self, server, name, **kwd):
#         self.server = server
#         self.name = name
#         self.namespace = name.strip().lower()
#         self.db = Redis(**(server.config))
#         self.ttl = kwd.get("ttl", None)
#         self.encoder = kwd.get("encoder", None)
#         self.decoder = kwd.get("decoder", None)
#         self.offline = False
#
#
#     def keygen(self, id):
#         return "%s:%s" % (self.namespace, id)
#
#
# class MixinClear:
#     def clear(self, *keys):
#         if self.offline is True:
#             return
#
#         if len(keys) == 0:
#             return
#
#         keys = util.unroll(keys) if len(keys) > 1 else [keys[0]]
#         if isinstance(keys[0], basestring) is False:
#             keys = map(str, keys)
#
#         keys = map(self.keygen, keys)
#         db = self.db
#         try:
#             if len(keys) == 1:
#                 db.delete(keys[0])
#             else:
#                 with db.pipeline() as pipeline:
#                     map(pipeline.delete, keys)
#                     pipeline.execute()
#         except Exception, ex:
#             log.error(FuzeError("Error deleting record from the database: %s" % ex.message, ex))
#             self.server.ping()
#
#
# class MixinExpire:
#     def expire(self, ttl, *keys):
#         db = self.db
#         try:
#             cnt = len(keys)
#             if cnt == 0:
#                 return
#
#             key = keys[0]
#             if isinstance(key, basestring) is False or key.find(":") == -1:
#                 if isinstance(key, basestring) is False:
#                     keys = map(str, keys)
#                 keys = map(self.keygen, keys)
#
#             for x in xrange(cnt):
#                 key = keys[x]
#                 db.expire(key, time=ttl)
#         except Exception, ex:
#             log.error(FuzeError("Error marking the ttl for the database record: %s" % ex.message, ex))
#             self.server.ping()
#
#
# class Bucket(Shard, MixinClear, MixinExpire):
#     def save(self, *objects):
#         if self.offline is True:
#             return False
#         if len(objects) == 0:
#             return True
#
#         objects = util.unroll(objects)
#         if len(objects) == 0:
#             return True
#
#
#         if util.is_model(objects[0]) is True:
#             objects = [(o.id, o) for o in objects]
#         elif isinstance(objects[0], tuple) is False:
#             raise FuzeError("The object list must either be a list of models or a list of key/val tuples!")
#
#         keys, vals = [o[0] for o in objects], [o[1] for o in objects]
#         if isinstance(keys[0], basestring) is False:
#             keys = map(str, keys)
#
#         keys = map(self.keygen, keys)
#
#         db, encoder = self.db, self.encoder
#         if encoder is not None:
#             vals = map(encoder, vals)
#
#         try:
#             cnt = len(keys)
#             for x in xrange(cnt):
#                 db.set(keys[x], vals[x])
#         except Exception, ex:
#             log.error(FuzeError("Error saving the database record: %s" % ex.message, ex))
#             self.server.ping()
#
#         ttl = self.ttl
#         if ttl is not None:
#             self.expire(ttl, keys)
#
#
#     def set(self, key, val):
#         self[key] = val
#
#     def get(self, key):
#         return self[key]
#
#     def __setitem__(self, key, value):
#         if self.offline is True:
#             return
#
#         if value is None:
#             self.clear(key)
#             return
#
#         db, encoder, ttl = self.db, self.encoder, self.ttl
#         key = self.keygen(key)
#         value = encoder(value) if encoder is not None else value
#
#         try:
#             db.set(key, value)
#         except Exception, ex:
#             log.error(FuzeError("Error saving the database record: %s" % ex.message, ex))
#             self.server.ping()
#             return
#
#         if ttl is not None:
#             self.expire(ttl, key)
#
#     def __getitem__(self, key):
#         if self.offline is True:
#             return None
#
#         db, decoder, ttl = self.db, self.decoder, self.ttl
#         if isinstance(key, basestring) is False:
#             key = str(key)
#         key = self.keygen(key)
#
#         object = None
#         try:
#             object = db.get(key)
#         except Exception, ex:
#             log.error(FuzeError("Error saving the database record: %s" % ex.message, ex))
#             self.server.ping()
#             return None
#
#         if object is not None:
#             if decoder is not None:
#                 object = decoder(object)
#
#             if ttl is not None:
#                 self.expire(ttl, key)
#
#         return object
#
#
