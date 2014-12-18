from . import system
from . import toolkit
from .topferral import *


class WebSession(object):
    __cookie_settings__ = {
        "name": "topferral",
        "timeout": 600,
        "secret": "topferral!",
        "path": "/",
        "secure": False
    }

    __slots__ = [
        "request",
        "__ctx__",
        "__token__",
        "__session__",
        "__storage__",
        "__cookie_queue__",
        "__active__"
    ]



    def __init__(self, *args):
        self.request = args[0]
        self.__ctx__ = None
        self.__session__ = None
        self.__cookie_queue__ = None
        self.__storage__ = None
        self.__token__ = None
        self.__active__ = False

    def activate(self):
        if self.__active__ is True:
            return self

        self.__ctx__ = toolkit.context()
        self.__ctx__.ip_address = self.request.client_addr
        self.__ctx__.user_agent_string = self.request.user_agent
        self.__active__ = True
        cookie = None
        try:
            cookie = self.request.cookies[self.cookie_config["name"]]
        except KeyError:
            pass

        if cookie is not None:
            try:
                cookie = self.__ctx__.codex.unseal(cookie)
                token = cookie["value"]

                if token != "0":
                    self.__session__ = self.__ctx__.sessions.restore(token)
                    # if self.__session__.token != token:
                    #     self.__append_cookie__(self.cookie_config["name"], self.__session__.token)
            except Exception, ex:
                message = "Error extracting cookie: %s" % ex.message
                print message

        if self.__session__ is not None:
            self.__token__ = self.__session__.token
        else:
            self.__session__ = self.__ctx__.sessions.create()
            self.__token__ = self.__session__.token
        self.__append_cookie__(self.cookie_config["name"], self.__token__)

        return self



    @property
    def token(self):
        return self.__token__

    @property
    def storage(self):
        storage = self.__storage__
        if storage is None:
            storage = {}
            self.__storage__ = storage
        return storage

    def refresh(self):
        ctx = self.__ctx__
        if ctx is None:
            return self
        self.__session__ = ctx.session
        self.__token__ = self.__session__.token if self.__session__ is not None else None
        if self.__token__ is not None:
            self.__append_cookie__(self.cookie_config["name"], self.__token__)


    def __append_cookie__(self, name, value, timeout=None):
        cookie_config = self.cookie_config
        if timeout is None:
            timeout = cookie_config["timeout"]
        else:
            timeout = (((timeout * 24) * 60) * 60)

        def __attach__(name, cookie, timeout, secure, response):
            if secure is False:
                response.set_cookie(
                    name,
                    value=cookie,
                    max_age=timeout
                )
                return response

            response.set_cookie(
                name,
                value=cookie,
                max_age=timeout,
                secure=True
            )
            return response

        ctx = self.__ctx__

        secure = cookie_config["secure"]
        try:
            cookie = ctx.codex.seal(value=value)
        except:
            cookie = toolkit.context().codex.seal(value=value)

        cookie_attach = toolkit.curry(__attach__, name, cookie, timeout, secure)
        if self.__cookie_queue__ is None:
            self.__cookie_queue__ = {}
        self.__cookie_queue__[name] = cookie_attach
        return self

    def attach_cookies(self, response):
        cookies = self.__cookie_queue__
        if not cookies:
            return self

        cookies = cookies.values()
        [cookie(response) for cookie in cookies]
        return self

    def nullify_session_cookie(self):
        self.__token__ = "0"
        self.__append_cookie__(self.cookie_config["name"], self.__token__)

    def logout(self):
        if self.__session__ is None:
            return

        self.__session__.destroy()
        self.nullify_session_cookie()
        self.__session__ = None


    # def logout(self):
    #     if self.authenticated is False:
    #         return
    #
    #     self.__ctx.logout()
    #     self.nullify_session_cookie()
    #     self.invalidate()

    @staticmethod
    def config_cookie(**kwd):
        cookie = WebSession.__cookie_settings__
        cookie["name"] = kwd["name"]
        cookie["path"] = kwd["path"]
        cookie["timeout"] = kwd["timeout"]
        cookie["secret"] = kwd["secret"]
        cookie["secure"] = kwd["secure"]

    @property
    def cookie_config(self):
        return WebSession.__cookie_settings__

    @property
    def response(self):
        return self.request.response

    def dispose(self):
        """Dispose of the session and related resources."""
        # try:
        #     self.__session__.clear()
        # except:
        #     pass
        self.__session__ = None
        self.__storage__ = None
        self.__ctx__ = None
        #tools.remove_context()


    # def __getattr__(self, method):
    #     fn = getattr(self.__ctx, method)
    #     return fn

    def invalidate(self):
        """ Invalidate the session.  The action caused by
        ``invalidate`` is implementation-dependent, but it should have
        the effect of completely dissociating any data stored in the
        session with the current request.  It might set response
        values (such as one which clears a cookie), or it might not."""
        #self.logout()
        #cookie = signed_serialize({"token": "-1"}, Session.Secret)
        #self.request.response.set_cookie("whodat", cookie, max_age=1)

        try:
            self.response.delete_cookie(self.cookie_config["name"])
        except:
            pass

            #self.request.response.delete_cookie(settings.cookie_name)
            #self.__ctx.logout()

    def changed(self):
        """ Mark the session as changed. A user of a session should
        call this method after he or she mutates a mutable object that
        is *a value of the session* (it should not be required after
        mutating the session itself).  For example, if the user has
        stored a dictionary in the session under the key ``foo``, and
        he or she does ``session['foo'] = {}``, ``changed()`` needn't
        be called.  However, if subsequently he or she does
        ``session['foo']['a'] = 1``, ``changed()`` must be called for
        the sessioning machinery to notice the mutation of the
        internal dictionary."""
        raise NotImplementedError()

    def flash(self, msg, queue='', allow_duplicate=True):
        storage = self.setdefault('_f_' + queue, [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)
            print storage
            # """ Push a flash message onto the end of the flash queue represented
            # by ``queue``.  An alternate flash message queue can used by passing
            # an optional ``queue``, which must be a string.  If
            # ``allow_duplicate`` is false, if the ``msg`` already exists in the
            # queue, it will not be readded."""
            # raise NotImplementedError()

    def pop_flash(self, queue=''):
        return self.pop('_f_' + queue, [])
        # """ Pop a queue from the flash storage.  The queue is removed from
        # flash storage after this message is called.  The queue is returned;
        # it is a list of flash messages added by
        # :meth:`pyramid.interfaces.ISesssion.flash`"""
        # raise NotImplementedError()

    def peek_flash(self, queue=''):
        temp = self.get('_f_' + queue, [])
        return temp
        # """ Peek at a queue in the flash storage.  The queue remains in
        # flash storage after this message is called.  The queue is returned;
        # it is a list of flash messages added by
        # :meth:`pyramid.interfaces.ISesssion.flash`
        # """
        # raise NotImplementedError()

    def new_csrf_token(self):
        """ Create and set into the session a new, random cross-site request
        forgery protection token.  Return the token.  It will be a string."""
        #token = str(uuid.uuid1())
        token = toolkit.guid(length=32)
        self.__token__ = token
        return token

    def get_csrf_token(self):
        """ Return a random cross-site request forgery protection token.  It
        will be a string.  If a token was previously added to the session via
        ``new_csrf_token``, that token will be returned.  If no CSRF token
        was previously set into the session, ``new_csrf_token`` will be
        called, which will create and set a token, and this token will be
        returned.
        """
        token = self.__token__
        if token is None:
            return self.new_csrf_token()
        return token

    # mapping methods
    def __getitem__(self, key):
        """Get a value for a key

        A ``KeyError`` is raised if there is no value for the key.
        """
        try:
            return self.__storage__.get(key)
        except:
            return None
        #return self.__state[key]

    def get(self, key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """

        try:
            return self.__storage__.get(key, default=default)
        except:
            return None

        #return self.__state.get(key, default)

    def __delitem__(self, key):
        """Delete a value from the mapping using the key.

        A ``KeyError`` is raised if there is no value for the key.
        """
        try:
            return self.__storage__.delete(key)
        except:
            return None
        return self.__session.delete(key)
        #self.__state.__delitem__(key)

    def __setitem__(self, key, value):
        """Set a new item in the mapping."""
        self.storage[key] = value
        #self.__state[key] = value

    def keys(self):
        """Return the keys of the mapping object.
        """
        try:
            return self.__storage__.keys()
        except:
            return []
        #return self.__state.keys()

    def values(self):
        """Return the values of the mapping object.
        """

        try:
            return self.__storage__.keys()
        except:
            return []
        return self.__session.state.values()
        #return self.__state.values()

    def items(self):
        """Return the items of the mapping object.
        """

        try:
            return self.__storage__.items()
        except:
            return []

    def iterkeys(self):
        """iterate over keys; equivalent to __iter__"""

        return self.storage.iterkeys()
        #return self.__state.iterkeys()

    def itervalues(self):
        """iterate over values"""

        return self.storage.itervalues()
        #return self.__state.itervalues()

    def iteritems(self):
        """iterate over items"""

        return self.storage.iteritems()

    def clear(self):
        """delete all items"""

        try:
            return self.__storage__.clear()
        except:
            pass

    def update(self, d):
        """ Update D from E: for k in E.keys(): D[k] = E[k]"""
        for key in d.keys():
            val = d[key]
            self.storage[key] = val

    def setdefault(self, key, default=None):
        """ D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D """
        #return self.__state.setdefault(key, default)
        return self.storage.setdefault(key, default)

    def pop(self, k, *args):
        """remove specified key and return the corresponding value
        ``*args`` may contain a single default value, or may not be supplied.
        If key is not found, default is returned if given, otherwise
        ``KeyError`` is raised"""
        #return self.__state.pop(k, *args)
        try:
            self.__storage__.pop(k, *args)
        except:
            pass


    def popitem(self):
        """remove and return some (key, value) pair as a
        2-tuple; but raise ``KeyError`` if mapping is empty"""
        #return self.__state.popitem()
        return self.__session.state.popitem()

    def __len__(self):
        """Return the number of items in the session."""
        #return self.__state.__len__()
        return 0 if self.__storage__ == None else len(self.__storage__)

    def __iter__(self):
        """Return an iterator for the keys of the mapping object."""
        #return self.__state.__iter__()
        return self.storage.__iter__()

    def __contains__(self, key):
        """Return true if a key exists in the mapping."""
        #return self.__state.__contains__(key)
        try:
            return self.__storage__.contains(key)
        except:
            return False

