from .error import StrataError



class AccessDeniedError(StrataError):
    type = "AccessDenied"

    def __init__(self, message, inner=None):
        StrataError.__init__(self, message, inner=inner)


class InvalidParameterError(StrataError):
    type = "InvalidParameter"

    def __init__(self, message, inner=None):
        StrataError.__init__(self, message, inner=inner)



class MissingParameterError(InvalidParameterError):
    type = "MissingParameter"

    def __init__(self, message, inner=None):
        InvalidParameterError.__init__(self, message, inner=inner)


class InvalidEmailError(StrataError):
    type = "InvalidEmail"

    def __init__(self, *args, **kwd):
        message = "Invalid email address."
        try:
            email = kwd["email"]
            kwd.pop("email")
            if isinstance(email, basestring):
                message = "%s [%s]" % (message, email)
        except:
            email = None if len(args) == 0 else args[0]
            if isinstance(email, basestring):
                message = "%s [%s]" % (message, email)
        StrataError.__init__(self, message, **kwd)


class RepositoryError(StrataError):
    type = "RepositoryError"

    def __init__(self, message, inner=None):
        StrataError.__init__(self, message, inner=inner)


class APIError(StrataError):
    type = "APIError"

    def __init__(self, message, inner=None):
        StrataError.__init__(self, message, inner=inner)