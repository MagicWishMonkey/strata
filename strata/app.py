from strata import *
from strata.context import Context
from strata.db.database import Database
from strata.db.redis_client import RedisClient


class App(object):
    __instance__ = None

    def __init__(self):
        self.__active__ = False
        self.__dbs__ = None

    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)

    @property
    def active(self):
        return self.__active__

    def db(self, *name):
        dbs = self.__dbs__
        assert dbs is not None, "The app is not initialized!"

        if len(name) == 0:
            return dbs[0][1].clone()
        name = name[0]
        for o in dbs:
            if o[0] == name:
                return o[1].clone()

        raise Exception("The requested database could not be found: %s" % name)

    def context(self):
        return Context(self)

    @staticmethod
    def create_context():
        app = App.__instance__
        if app.active is False:
            app.load()
        return app.context()

    @staticmethod
    def get():
        return App.__instance__


@App.plugin
def load(self):
    if self.__active__ is True:
        print "Already loaded!"

    log = system.log
    settings = system.settings
    if settings is None:
        log.info("The settings file is not specified. Skipping.")
        self.__active__ = True
        return self

    def init_dbs(self, settings):
        dbs = []
        databases = settings.databases
        for name in databases:
            db_cfg = databases[name]
            db_cfg["label"] = "%s:%s" % (db_cfg["driver"], name)
            driver = db_cfg["driver"]
            if driver == "redis":
                db = RedisClient.open(**(db_cfg))
                dbs.append((name, db))
                continue
            db = Database.open(**(db_cfg))
            dbs.append((name, db))
            if name == "default":
                if len(dbs) > 1:
                    dbs.reverse()
        self.__dbs__ = dbs

    init_dbs(self, settings)
    self.__active__ = True


App.__instance__ = App()