from .. import toolkit



class Query(object):
    def __init__(self, sql, params=None, tokens=None, key=None, db=None):
        self.key = key
        self.sql = sql
        self.params = params
        self.tokens = tokens
        self.db = db

        self.result = None
        self.error = None
        self.tag = None

        self.adapter = None
        # self.transaction = None
        # self.action = None
        self.auto_cast = True
        # self.remap_columns = False

    # def remap(self):
    #     """Remap the column names to fit our namespace"""
    #     self.remap_columns = True
    #     return self

    # def rerun(self):
    #     target = self.action
    #     method = tools.Reflect.get_method(self, target)
    #     return method()

    def swap(self, token, value):
        sql = self.sql
        if isinstance(value, basestring) is False:
            if value is None:
                value = "null"
            else:
                value = str(value)
        while sql.find(token) > -1:
            sql = sql.replace(token, value)
        self.sql = sql
        return self

    def set_tag(self, tag):
        self.tag = tag
        return self

    def set_db(self, db):
        self.db = db
        return self

    def set_param(self, key, val):
        if self.params is None:
            self.params = {}
        self.params[key] = val
        return self

    def bind(self, obj):
        if obj is None:
            return self
        if self.tokens is None:
            return self

        try:
            self.params = {}
            if obj is None:
                return self

            for token in self.tokens:
                name = token.name
                param = obj.get(name, None)
                if isinstance(param, (list, dict)) is True:
                    param = toolkit.json(param)
                self.params[name] = param
        except Exception, ex:
            raise ex

            # raise DatabaseQueryException(
            #     message="An error occurred while binding the object to the query. %s" % ex.message,
            #     inner=ex,
            #     query=self,
            #     database=self.db,
            #     ctx=self.ctx
            # )
        return self

    def try_insert(self, fn=None):
        try:
            return self.insert(fn)
        except Exception, ex:
            print "Insert failed-> %s" % ex.message
            return None

    # @staticmethod
    # def database_not_available_error(qry):
    #     return DatabaseQueryException(
    #         message="The database reference has not been assigned!",
    #         query=qry,
    #         database=qry.db,
    #         ctx=qry.ctx
    #     )

    @property
    def database(self):
        database = self.db
        if database:
            return database
        raise Query.database_not_available_error(self)

    def multiple(self, *values):
        self.db.executemany(self, *values)

    def insert(self, fn=None):
        id = self.database.insert(self)
        if id:
            if fn:
                return fn(id)
        return id

    def try_update(self):
        try:
            self.update()
            return True
        except Exception, ex:
            print "update failed-> %s" % ex.message
            return False

    def update(self):
        # self.type = QueryType.Execute
        return self.database.update(self)

    def try_execute(self):
        try:
            self.execute()
            return True
        except Exception, ex:
            print "execute failed-> %s" % ex.message
            return False

    def execute(self):
        # self.type = QueryType.Execute
        return self.database.execute(self)

    # def run(self):
    #     txt = self.sql.lower()
    #     ix = self.sql.lower().find("select ")
    #     if ix > -1:
    #         return self.select()
    #     return self.execute()

    def record(self, auto_cast=True, adapter=None):
        lst = self.select(adapter=adapter, auto_cast=auto_cast)
        return lst[0] if len(lst) > 0 else None

    def select(self, adapter=None, auto_cast=True):
        #self.set_action("select", type=QueryType.Select)
        #self.type = QueryType.Select
        if adapter is not None:
            self.adapter = adapter
        else:
            adapter = self.adapter

        self.auto_cast = auto_cast
        result = self.database.select(self)
        if adapter is not None:
            result = map(adapter, result)

        self.result = result

        # if self.remap_columns is True:
        #     if len(self.result) > 0 and isinstance(self.result[0], dict) is True:
        #         columns = self.result[0].keys()
        #         mapping = {}
        #         for column in columns:
        #             mapping[column] = tools.make_pep_compliant(column)
        #
        #         tools.remap_column_names(self.result, **(mapping))

        return self.result

    def scalar(self, auto_cast=True):
        return self.get_scalar(auto_cast=auto_cast)

    def scalars(self, auto_cast=True):
        return self.get_scalars(auto_cast=auto_cast)

    def get_scalar(self, fn=None, auto_cast=True):
        lst = self.get_scalars(auto_cast=auto_cast)
        if fn:
            return fn(lst[0]) if len(lst) > 0 else None
        return lst[0] if len(lst) > 0 else None

    def get_scalars(self, fn=None, auto_cast=True):
        lst = self.select(auto_cast=auto_cast)
        if lst is None:
            return []
        if fn:
            return map(fn, lst)
        return lst

    def get_record_list(self, adapter=None, auto_cast=True):
        if adapter is None:
            adapter = self.adapter
        return self.select(adapter=adapter, auto_cast=auto_cast)

    def get_record(self, adapter=None, auto_cast=True):
        records = self.get_record_list(adapter, auto_cast=auto_cast)
        return None if len(records) == 0 else records[0]

    @staticmethod
    def create(sql, params=None):
        qry = parse(sql, params=params)
        return qry

    def clone(self, obj=None, db=None, deep=False):
        qry = Query(self.sql, params=self.params, tokens=self.tokens, key=self.key)
        if obj:
            return qry.bind(obj)
        if db is not None:
            qry.db = db
        if deep is True:
            if qry.db is None:
                qry.db = self.db
            qry.ctx = self.ctx
            qry.tag = self.tag
        return qry

    def duplicate(self, obj=None):
        qry = self.clone(obj=obj)
        qry.db = self.db
        qry.tag = self.tag
        return qry

    def where(self, pattern=None, values=None, conjunction="OR"):
        if len(values) == 1 and isinstance(values, (tuple, list)) is True:
            values = values[0]
        if pattern is not None and pattern == "id=@id":
            if len(values) == 1:
                sql = self.sql.strip()
                while sql.endswith(";"):
                    sql = sql[:-1]
                sql = "{sql} WHERE id={id};".format(sql=sql, id=values[0])
                self.sql = sql
                #print sql
                return self

        if pattern is not None and values is not None:
            if isinstance(values, list) is True:
                conjunction = "IN"


        if values is None:
            if isinstance(pattern, dict):
                sql = self.sql.strip()
                while sql.endswith(";"):
                    sql = sql[:-1]

                keys = pattern.keys()
                conditions = []
                for key in keys:
                    val = pattern[key]
                    if val is None:
                        val = "null"
                    elif isinstance(val, basestring):
                        val = "'%s'" % val
                    else:
                        val = "%s" % str(val)

                    try:
                        condition = "%s=%s" % (key, val)
                        conditions.append(condition)
                    except:
                        condition = "%s=%s" % (str(key), val)
                        conditions.append(condition)

                where_clause = " AND ".join(conditions)
                sql = "%s WHERE %s;" % (sql, where_clause)
                self.sql = sql
                print sql
                return self
            return self

        sql = self.sql
        if isinstance(values, list) is False:
            values = [values]

        pattern_parts = pattern.split('@')
        pattern_column = pattern_parts[0].split('=')[0]
        token = "@%s" % pattern_parts[1].split(' ')[0]
        if values is None or len(values) == 0:
            if sql.strip().endswith(";"):
                return self
            self.sql += ";"
            return self

        clause_suffix = None
        ix = sql.lower().find("group by")
        if ix > -1:
            clause_suffix = sql[ix:]
            sql = sql[:ix]

        def wrap(txt):
            if txt is None or len(txt) == 0:
                return "null"
            return "'%s'" % toolkit.sql_sanitize(txt)


        while sql.endswith(";"):
            sql = sql[:-1]

        prefix = "WHERE"
        suffix = ";"
        if sql.lower().find(" where") > -1:
            prefix = " "

        if sql.lower().find("where") > 0:
            prefix = "AND("
            suffix = ");"

        numbers = False
        if isinstance(values[0], (int, long)):
            numbers = True
            values = [v for v in values if v is not None]
            values = map(str, values)
        else:
            values = map(wrap, values)

        buffer = []
        buffer.append(sql)
        buffer.append(" ")
        buffer.append(prefix)
        buffer.append(" ")
        if conjunction == "IN":
            csv = ",".join(values)
            buffer.append("%s IN (%s)" % (pattern_column, csv))
        else:
            snippets = []
            for x in xrange(len(values)):
                value = values[x]
                snip = pattern.replace(token, value)
                snippets.append(snip)

            conjunction = " %s " % conjunction
            txt = conjunction.join(snippets)
            buffer.append(txt)

        if clause_suffix is not None:
            if suffix.endswith(";"):
                suffix = suffix[:len(suffix)-1]
            suffix = "%s %s" % (suffix, clause_suffix)

        buffer.append(suffix)
        if suffix.endswith(";") is False:
            buffer.append(";")
        sql = "".join(buffer)
        self.sql = sql
        return self


    def limit(self, quantity):
        sql = self.sql
        if sql.strip().endswith(";"):
            sql = sql.strip()
            sql = sql[0:len(sql)-1]

        sql = "%s LIMIT %d;" % (sql, quantity)
        self.sql = sql
        return self

    def order_by(self, field, direction="DESC"):
        if direction.strip().lower() != "desc":
            direction = "ASC"
        clause = "ORDER BY %s %s" % (field, direction)
        sql = self.sql
        if sql.strip().endswith(";"):
            sql = sql.strip()
            sql = sql[0:len(sql)-1]

        sql = "%s %s;" % (sql, clause)
        self.sql = sql
        return self

    # def freeze(self):
    #     object = {
    #         "sql": self.sql,
    #         "params": self.params,
    #         "tokens": self.tokens,
    #         "tag": self.tag,
    #         "key": self.key
    #     }
    #     blob = tools.pickle(object)
    #     blob = tools.base64_encode(blob)
    #     return blob


    # def restore(self, blob):
    #     object = tools.unpickle(tools.unbase64(blob))
    #     self.sql = object["sql"]
    #     self.params = object["params"]
    #     self.tokens = object["tokens"]
    #     self.key = object["key"]
    #     self.tag = object["tag"]
    #     return self



    def stringify(self):
        sql = self.sql
        while sql.find("\n") > -1:
            sql = sql.replace("\n", " ")
        while sql.find("\r") > -1:
            sql = sql.replace("\r", " ")
        while sql.find("\t") > -1:
            sql = sql.replace("\t", " ")
        while sql.find("  ") > -1:
            sql = sql.replace("  ", " ")

        for token in self.tokens:
            name = token.name
            sql = sql.replace(":{token}".format(token=name), "@{token}".format(token=name))


        params = self.params
        if params is None:
            return sql
        params = toolkit.json(params)
        return "{sql}\t{params}".format(sql=sql, params=params)



    def replace(self, token, value):
        if isinstance(value, basestring):
            self.sql = self.sql.replace(token, "'%s'" % value)
        elif value is None:
            self.sql = self.sql.replace(token, "null")
        else:
            self.sql = self.sql.replace(token, toolkit.stringify(value))
        return self

    def trace(self, *columns):
        columns = toolkit.unroll(columns)
        rows = self.get_object_list()
        width = len(columns)
        height = len(rows)
        if width == 0:
            if height == 0:
                print "n/a"
                return
            r = rows[0]
            columns = r.keys()
            width = len(columns)

        for x in xrange(height):
            line = []
            r = rows[x]
            for y in xrange(width):
                column = columns[y]
                value = r[column]
                if value is None:
                    value = "null"
                elif isinstance(value, basestring) is False:
                    value = str(value).ljust(13, " ")
                else:
                    value = value.ljust(0, " ")
                line.append(value)
            line = "".join(line)
            print line

    def __repr__(self):
        if self.key:
            return "%s -> %s" % (self.key, self.sql)
        return self.sql

    @staticmethod
    def new(sql, params=None):
        return Query.create(sql, params)


# def create(sql, params=None):
#     return Query(sql, params=params)


def parse(txt, params=None):
    if txt.find("@") == -1:
        return Query(txt, params=params)

    filtered = []
    ignore = False
    prev = ''
    for c in txt:
        if c == '\r' or c == '\n':
            if ignore:
                ignore = False
        else:
            if c == '-' and prev == '-':
                ignore = True
                filtered.pop()

        if ignore is False:
            filtered.append(c)

        prev = c

    sql = ''.join(filtered).rstrip()
    max = len(sql)
    capture = False
    buffer = []
    tokens = []
    tokenBegin = 0
    tokenEnd = 0
    tokenIndex = {}
    tokenBuffer = None
    prev = ''
    ix = 0
    for c in sql:
        ix = (ix + 1)
        if c == ' ' or c == ',' or c == ';' or c == ')' or c == '\'' or c == '\r' or c == '\n':
            if capture:
                capture = False
                tokenEnd = ix
                tokens.append(Token(tokenBuffer, start_ix=tokenBegin, end_ix=tokenEnd))
                tokenBuffer = ""
                tokenBegin = 0
                tokenEnd = 0
            buffer.append(c)
        else:
            if capture:
                tokenBuffer += c
            else:
                if c == '@':
                    capture = True
                    tokenBuffer = ""
                    tokenBegin = ix
                    buffer.append("?")
                else:
                    buffer.append(c)

        prev = c

    if tokenBegin and len(tokenBuffer) > 0:
        tokens.append(Token(tokenBuffer, start_ix=tokenBegin, end_ix=ix))
        tokenBuffer = None

    sql = ''.join(buffer)

    try:
        buffer = []
        ix = 0
        for c in sql:
            if c == '?':
                buffer.append(':%s' % tokens[ix].name)
                ix = (ix + 1)
            else:
                buffer.append(c)

        sql = ''.join(buffer)
        query = Query(sql, params=params)
        query.tokens = tokens
    except Exception, ex:
        raise ex
    return query


class Token(object):
    __slots__ = [
        "name",
        "start_ix",
        "end_ix"
    ]
    def __init__(self, name, start_ix=0, end_ix=0):
        self.name = name
        self.start_ix = start_ix
        self.end_ix = end_ix

    @property
    def length(self):
        return (self.end_ix - self.start_ix)

    def __repr__(self):
        return "Token-> %s" % self.name