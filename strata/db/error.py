from ..errors import FuzeError


class DatabaseError(FuzeError):
    type = "DatabaseError"

    def __init__(self, message, sql=None, params=None, inner=None):
        try:
            if message[0] == "(":
                ix = message.find(") (")
                txt = message[ix + 3:]
                parts = txt.split(",")
                if parts[0].isdigit():
                    txt = ",".join(parts[1:])
                if txt.endswith(")"):
                    txt = txt[0:len(txt) - 1]
                message = txt.strip()
        except:
            pass

        if sql is not None:
            statement = [sql]
            if params is not None:
                try:
                    from .. import toolkit
                    params = toolkit.json(params, indent=2)
                    statement.append(params)
                except:
                    pass
            statement = "\n".join(statement)
            message = "%s\n%s" % (message, statement)

        FuzeError.__init__(self, message, inner=inner)


class DatabaseQueryError(DatabaseError):
    type = "DatabaseQueryError"

    def __init__(self, message, sql=None, params=None, inner=None):
        DatabaseError.__init__(self, message, sql=sql, params=params, inner=inner)