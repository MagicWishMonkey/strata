from strata import *
from strata.context import Extension
from strata.types import IRepository
from strata.types import MetaRepository
from strata.types import MetaModel



class Repository(IRepository, Extension):
    __metaclass__ = MetaRepository
    __select_query__ = None
    __insert_query__ = None
    __update_query__ = None
    __delete_query__ = None
    __lookup_query__ = None
    __table_name__ = None
    __cache_config__ = {
        "ttl": 60,
        "encoder": toolkit.serialize,
        "decoder": toolkit.deserialize,
        "adapter": None
    }

    def __init__(self, *ctx):
        Extension.__init__(self, *ctx)
        self.label = self.__class__.__name__
        self.__cache__ = None


    @property
    def cache(self):
        cache = self.__cache__
        if cache is not None:
            return cache

        bucket = self.redis.get(self.__class__.__name__.lower())
        if bucket is None:
            cfg = self.__cache_config__
            try:
                if cfg["name"] is None:
                    cfg["name"] = self.__class__.__name__.lower()
            except:
                cfg["name"] = self.__class__.__name__.lower()
                if cfg.get("keygen", None) is None:
                    cfg["keygen"] = self.__class__.gen_uri

            if self.__class__.__table_name__ is None:
                self.__class__.__table_name__ = self.table_name
            bucket = self.redis.bucket(
                cfg["name"],
                ttl=cfg["ttl"],
                encoder=cfg["encoder"],
                decoder=cfg["decoder"],
                adapter=cfg["adapter"],
                keygen=cfg["keygen"]
            )
        self.__cache__ = bucket
        return bucket


    def initialize(self):
        pass


    @property
    def model_spawn(self):
        model_class = self.model_class
        if model_class is None:
            return lambda o: o
        return model_class.create

    def select_query(self, *keys):
        sql = self.__class__.__select_query__
        assert sql is not None, "The select query is not specified for %s" % self.label

        model_class = self.model_class
        query = self.query(sql)
        if model_class is not None:
            query.adapter = model_class.create

        if len(keys) == 0:
            return query

        query.where("id=@id", keys)
        return query

    def lookup_query(self, *keys):
        sql = self.__class__.__lookup_query__
        if sql is None:
            table_name = self.table_name
            sql = "SELECT ID as id FROM %s WHERE Label=@label;" % table_name
            self.__class__.__lookup_query__ = sql

        query = self.query(sql)
        if len(keys) == 0:
            return query

        query.where("label=@label", keys)
        return query

    @property
    def table_name(self):
        table_name = self.__class__.__table_name__
        if table_name is None:
            table_name = self.label.lower()
            table_name = table_name[0:len(table_name) - 1]
            self.__class__.__table_name__ = table_name
        return table_name

    #
    # @property
    # def label(self):
    #     return self.__class__.__name__


    def lookup(self, *keys):
        single = True if len(keys) == 0 \
                         or len(keys) == 1 \
                            and isinstance(keys[0], list) is False else []


        keys = util.unroll(keys)
        if len(keys) == 0:
            return None if single is True else []

        query = self.lookup_query(keys)
        keys = query.scalars()
        if single is True:
            return keys[0] if len(keys) > 0 else None
        return keys

    def get(self, *keys):
        if len(keys) == 0:
            return None

        single = False
        if len(keys) == 1:
            if isinstance(keys[0], list) is False:
                single = True

        keys = util.unroll(keys)
        if len(keys) == 0:
            return []

        if isinstance(keys[0], basestring) is True:
            if keys[0].isdigit() is True:
                keys = map(int, keys)
            else:
                keys = self.lookup(keys)

        cache = self.cache
        cached = cache.fetch(keys)
        if len(cached) > 0:
            trace(len(cached), "objects in", self.label, "cache")
            #trace("%s objects in cache." % str(len(cached)))
            if len(cached) == len(keys):
                if single is True:
                    return cached[0] if len(cached) > 0 else None
                return cached

        if len(cached) > 0:
            cache_keys = set([c.id for c in cached])
            keys = [k for k in keys if k not in cache_keys]

        query = self.select_query(keys)
        models = query.select()
        if len(models) > 0:
            cache.save(models)

        if cached:
            models.extend(cached)

        if single is True:
            return models[0] if len(models) > 0 else None
        return models

    @classmethod
    def gen_uri(cls, model):
        table_name = cls.__table_name__
        if isinstance(model, int) is True:
            return "%s#%s" % (table_name, str(model))

        try:
            return "%s#%s" % (table_name, str(model.id))
        except Exception, ex:
            if isinstance(model, basestring) is True:
                if model.isdigit() is True:
                    return "%s#%s" % (table_name, str(model))
            raise ex

    def __str__(self):
       return "%s" % self.label

    def __repr__(self):
        return self.__str__()


def keygen(cls, model):
    table_name = cls.__table_name__
    try:
        return "%s#%s" % (table_name, str(model.id))
    except Exception, ex:
        if isinstance(model, int) is True:
            return "%s#%s" % (table_name, str(model))
        raise ex