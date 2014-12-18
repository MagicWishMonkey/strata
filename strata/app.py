from . import system
from . import toolkit
from .context import Context
from .toolkit.structs import *
from .toolkit.codex import Codex
from .db import *



class App(object):
    __instance__ = None

    def __init__(self):
        self.__active__ = False
        self.__db__ = None
        self.__redis__ = None
        self.__smtp__ = None
        self.__dirs__ = None
        self.__config__ = None
        self.__codex__ = None
        # self.__admins__ = None
        self.__workspace__ = None

    @property
    def admins(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return system.admins

    @property
    def config(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return self.__config__

    @property
    def codex(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        codex = self.__codex__
        codex = codex.clone()
        return codex

    @property
    def db(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        db = self.__db__
        if db is None:
            raise Exception("The database has not been configured.")
        return db

    @property
    def redis(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        redis = self.__redis__
        if redis is None:
            raise Exception("The redis database has not been configured.")
        return redis

    @property
    def smtp(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return self.__smtp__

    @property
    def dirs(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return self.__dirs__

    @property
    def shared_folder(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return self.__dirs__.shared

    def context(self):
        if self.__active__ is False:
            raise Exception("The application has not been initialized.")
        return Context(self)

    @staticmethod
    def create_context():
        app = App.__instance__
        return app.context()

    @staticmethod
    def setup():
        if App.__instance__ is not None:
            return App.__instance__

        app = App()
        App.__instance__ = app
        system.application = app
        return app

    def load(self, workspace):
        if self.__active__ is True:
            raise Exception("The app has already been initialized.")

        if isinstance(workspace, basestring) is True:
            workspace = toolkit.folder(workspace)

        if workspace.exists is False:
            raise Exception("The workspace does not exist: %s" % workspace.uri)

        settings = workspace.file("settings.json")
        if settings.exists is False:
            raise Exception("The settings.json file does not exist: %s" % settings.uri)

        config = toolkit.unjson(settings.read_text())
        config = Wrapper.create(config)

        override = workspace.file("settings.override.json")
        if override.exists is True:
            override = toolkit.unjson(override.read_text())
            config.override(override)#Wrapper.create(config))

        system.flags.bind(**(config.flags))
        if system.flags.quarantine is True:
            system.quarantine = True

        app_cfg = config.application
        system.app_uri = app_cfg.uri
        system.app_name = app_cfg.name
        system.workspace = workspace
        system.default_member_avatar = app_cfg.default_member_avatar

        administrators = app_cfg.administrators
        if administrators:
            if isinstance(administrators, list) is False:
                administrators = [administrators]

            for x, admin in enumerate(administrators):
                person = toolkit.Person(admin)
                if person is None or person.email is None:
                    raise Exception("Invalid administrator format: %s" % admin)
                administrators[x] = person

        if administrators:
            system.admins = administrators

        # init the codex module
        key_cfg = config.keychain
        self.__codex__ = Codex(
            salt=str(key_cfg.salt),
            weak=str(key_cfg.weak),
            strong=str(key_cfg.strong),
            hmac=str(key_cfg.hmac)
        )

        # init the db module
        db_cfg = config.database
        if db_cfg.params is not None:
            db_cfg.params = db_cfg.params.reduce()

        self.__db__ = Database.open(
            driver=db_cfg.driver,
            server=db_cfg.server,
            port=db_cfg.port,
            database=db_cfg.database,
            username=db_cfg.username,
            password=db_cfg.password,
            params=db_cfg.params
        )

        # init the smtp module
        smtp_cfg = config.smtp

        dir_cfg = config.directories
        directories = {}
        for name in dir_cfg:
            uri = dir_cfg[name]
            directories[name] = toolkit.folder(uri)

        self.__dirs__ = Wrapper(directories)
        self.__workspace__ = workspace
        self.__config__ = config

        self.__active__ = True
        system.seal()

        return self.context()





app = App.setup()