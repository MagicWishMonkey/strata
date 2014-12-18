#from fuze import *
from . import system
from . import toolkit
from .threads import current_thread



class Context(object):
    __slots__ = [
        "__uuid__",
        "__bag__",
        "__member__",
        "__session__",
        "ip_address",
        "user_agent_string"

    ]

    def __init__(self, app):
        self.__uuid__ = toolkit.guid(12)
        self.__bag__ = None
        self.__member__ = None
        self.__session__ = None
        self.ip_address = None
        self.user_agent_string = None
        current_thread.set("context", self)

    @property
    def uuid(self):
        return self.__uuid__

    @property
    def bag(self):
        bag = self.__bag__
        if bag is None:
            bag = {}
            self.__bag__ = bag
        return bag

    @property
    def app(self):
        app = system.application
        if app is None:
            raise Exception("The application has not been initialized.")
        return app

    @property
    def member(self):
        member = self.__member__
        if member is None:
            session = self.__session__
            if session is None:
                return None
            return session.member
        return member

    @property
    def member_id(self):
        member = self.__member__
        if member is None:
            return None
        return member.id

    @property
    def session(self):
        session = self.__session__
        return session

    @property
    def session_id(self):
        session = self.__session__
        if session is None:
            return None
        return session.id

    @property
    def authenticated(self):
        if self.__member__ is None:
            return False
        return True

    def attach(self, session):
        if session is None:
            self.__session__ = None
            self.__member__ = None
            return self

        #current_session = self.session
        if self.member_id != session.member_id:
            self.__member__ = session.member
        self.__session__ = session
        return self


    def clear(self):
        self.__session__ = None
        self.__member__ = None
        self.__bag__ = None
        return self

        # if isinstance(session, toolkit.Person):
        #     member = session
        #     current_member = self.__member__
        #     if member == current_member:
        #         return self
        #     self.__member__ = member
        #     if current_session is not None:
        #         if current_session.member != member:
        #             self.__session__ = None
        #             return self
        # # elif isinstance(session, Session):
        # #     if current_session is not None:
        # #         if current_session == session:
        # #             return self
        # #
        # #     self.__session__ = session
        # return self

    @property
    def config(self):
        return self.app.config

    @property
    def codex(self):
        bag = self.bag
        try:
            return bag["codex"]
        except:
            codex = self.app.codex
            bag["codex"] = codex
            return codex

    @property
    def db(self):
        bag = self.bag
        try:
            return bag["db"]
        except:
            db = self.app.db
            bag["db"] = db
            return db

    @property
    def redis(self):
        bag = self.bag
        try:
            return bag["redis"]
        except:
            redis = self.app.redis
            bag["redis"] = redis
            return redis

    def query(self, sql, *args, **params):
        if len(args) > 0 and isinstance(args[0], dict) is True:
            kwd = args[0]
            for key in kwd.keys():
                params[key] = kwd[key]
        return self.db.query(
            sql,
            **params
        )

    def query_buffer(self):
        return self.db.query_buffer()

    def get_extension(self, name, cls):
        bag = self.bag
        try:
            return bag[name]
        except:
            ext = cls(self)
            bag[name] = ext
            return ext

    @staticmethod
    def current():
        ctx = current_thread.get("context")
        if ctx is not None:
            return ctx

        app = system.application
        ctx = app.context()
        return ctx



    def __repr__(self):
        member = self.__member__
        if member is None:
            return "Context#%s" % self.__uuid__
        return "Context#%s - %s" % (self.__uuid__, member.username)

    def __str__(self):
        return self.__repr__()


class Extension(object):
    def __init__(self, *args):
        self.ctx = args[0] if len(args) > 0 else toolkit.context()

    def __getattr__(self, method):
        fn = getattr(self.ctx, method)
        return fn

    def scalars(self, sql, *args, **params):
        return self.ctx.query(sql, *args, **params).scalars()

    def scalar(self, sql, *args, **params):
        return self.ctx.query(sql, *args, **params).scalar()

    def fetch(self, sql, *args, **params):
        return self.ctx.query(sql, *args, **params).select()

    def query(self, sql, *args, **params):
        return self.ctx.query(sql, *args, **params)

    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)