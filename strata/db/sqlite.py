import sqlite3
from strata import util


class SQLite(object):
    def __init__(self, uri, constructor=None):
        self.uri = uri
        if util.file(uri).exists is False:
            if uri.lower().endswith(".sqlite") is False:
                uri = "{uri}.sqlite".format(uri=uri)
                self.uri = uri

            data = util.unbase64("U1FMaXRlIGZvcm1hdCAzAAQAAQEAQCAgAAAAAQAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAC3mAQ0AAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==")
            file = util.file(uri)
            file.write_data(data)
            self.execute("""
            CREATE TABLE "sequences" (
                 "id" INTEGER NOT NULL,
                PRIMARY KEY("id")
            );""")
            self.create_default_schema()
            if constructor is not None:
                constructor(self)

    def create_default_schema(self):
        pass

    def connect(self):
        return sqlite3.connect(self.uri)

    def parse(self, sql, **params):
        keys = params.keys()
        args = None
        if len(keys) > 0:
            args = []
            for key in keys:
                token = "@%s" % key
                ix = sql.find(token)

                #sql = sql.replace(token, "?")

                val = params[key]
                if isinstance(val, basestring) is True:
                    try:
                        val = str(val)
                    except:
                        try:
                            val = util.text.to_unicode(val)
                        except:
                            val = val.encode('ascii', 'ignore')
                elif val is None:
                    val = "null"
                args.append({"ix": ix, "token": token, "name": key, "value": val})

            for arg in args:
                ix = arg["ix"]
                sql = sql.replace(arg["token"], "?")


            args = sorted(args, key=lambda o: o["ix"])
            args = [arg["value"] for arg in args]
            args = (args)

        return (sql, args)

    def update(self, sql, **params):
        if sql.find("@id") > -1:
            if params.get("id", None) is None:
                id = self.sequence()
                sql = sql.replace("@id", str(id))
        return self.execute(sql, **params)

    def insert(self, sql, **params):
        if params.get("id", None) is None:
            if sql.find("@id") > -1:
                params["id"] = self.sequence()
        return self.execute(sql, **params)

    def execute(self, sql, **params):
        sql, args = self.parse(sql, **params)
        connection = sqlite3.connect(self.uri)
        cursor = connection.cursor()
        if args is None:
            o = cursor.execute(sql)
        else:
            o = cursor.execute(sql, args)

        rowid, rowcount = None, None
        try:
            rowcount = o.rowcount
        except:
            pass
        try:
            rowid = o.lastrowid
        except:
            pass

        connection.commit()
        if rowcount is not None:
            return rowcount
        if rowid is not None:
            return rowid
        return self

    def tables(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = self.scalars(sql)
        return tables

        #for x, table in enumerate(tables):
        #    table_schema = self.schema(table)
        #    tables[x] = table_schema
        #return tables

    def schema(self, table):
        def draw_table(*objects, **kwd):
            from prettytable import PrettyTable

            fields = kwd.get("fields", None)
            alias = kwd.get("alias", None)
            objects = util.unroll(objects)
            if len(objects) == 0:
                table = PrettyTable([])
                print table
                return

            if isinstance(objects[0], (int, long)) is True:
                objects = [{"id": o} for o in objects]
            elif isinstance(objects[0], basestring) is True:
                objects = [{"value": o} for o in objects]
            #elif is_model(objects[0]) is True:
            #    objects = [o.dictionary() for o in objects]

            def sort_cols(columns):
                ordered = []
                column_table = dict((c.lower(), c) for c in columns)
                if column_table.get("id", None) is not None:
                    ordered.append(column_table["id"])
                if column_table.get("label", None) is not None:
                    ordered.append(column_table["label"])
                if column_table.get("name", None) is not None:
                    ordered.append(column_table["name"])
                if column_table.get("username", None) is not None:
                    ordered.append(column_table["username"])

                column_table = dict((c, None) for c in ordered)
                for column in columns:
                    if column not in column_table:
                        ordered.append(column)
                return ordered


            if alias is not None:
                keys = alias.keys()
                for o in objects:
                    for key in keys:
                        o[alias[key]] = o[key]
                        o.pop(key)



            columns = objects[0].keys()
            if fields is not None:
                columns = fields

            order = kwd.get("order", None)
            if order is not None:
                order = order.split(",")
                order = [o.strip() for o in order]
                order_table = {}
                for x in xrange(len(columns)):
                    order_table[columns[x]] = (x, columns[x])

                for x in xrange(len(order)):
                    if order_table.get(order[x], None) is not None:
                        order_table[order[x]] = (x, order[x])

                ordered = order_table.values()
                ordered = sorted(ordered, key=lambda o: o[0], reverse=False)
                columns = [o[1] for o in ordered]


            transforms = {}
            columns = sort_cols(columns)
            table = PrettyTable(columns)
            table.padding_width = 1
            for column in columns:
                table.align[column] = "l"
                xform = kwd.get(column, lambda o: o)
                transforms[column] = xform

            for o in objects:
                values = []
                for column in columns:
                    val = o[column]
                    val = transforms[column](val)
                    if isinstance(val, basestring) is True:
                        if len(val) > 100:
                            val = "%s..." % val[:100]
                            #val = "{val}...".format(val=val[:100])
                    elif val is None:
                        val = "null"
                    values.append(val)
                table.add_row(values)

            return table

        table = table.strip().replace(";", "")
        sql = "PRAGMA table_info(%s);" % table.strip()
        records = self.select(sql)
        columns = []
        for r in records:
            name = r["name"]
            type = r["type"]
            columns.append({"name": name, "type": type})

        table = draw_table(*(columns))
        txt = table.__str__()
        return txt

    def query_buffer(self):
        return QueryBuffer(self)

    def sequence(self, *count):

        offset = self.scalar("SELECT id FROM sequences ORDER BY id DESC LIMIT 1;")
        if offset is None:
            #self.insert("INSERT INTO sequences (id) VALUES (1);")
            offset = 0

        if len(count) == 0 or count[0] < 2:
            id = (offset + 1)
            self.insert("INSERT INTO sequences (id) VALUES ({id});".format(id=id))
            return id

        count = (count[0] - 1)
        id = (offset + 1)
        keys = [id]
        queries = ["INSERT INTO sequences (id) VALUES ({id});".format(id=id)]
        for x in xrange(count):
            id = (id + 1)
            keys.append(id)
            queries.append("INSERT INTO sequences (id) VALUES ({id});".format(id=id))

        connection = sqlite3.connect(self.uri)
        cursor = connection.cursor()
        map(cursor.execute, queries)
        connection.commit()
        return keys

    def scalar(self, sql, **params):
        objects = self.scalars(sql, **params)
        return objects[0] if len(objects) > 0 else None

    def scalars(self, sql, **params):
        objects = self.select(sql, **params)
        if len(objects) > 0:
            if isinstance(objects[0], dict) is True:
                object = objects[0]
                column = object.keys()[0]
                objects = [o[column] for o in objects]
        return objects

    def record(self, sql, *fn, **params):
        objects = self.select(sql, *fn, **params)
        return objects[0] if len(objects) > 0 else None

    def select(self, sql, *fn, **params):
        adapter = None if len(fn) == 0 else fn[0]

        sql, args = self.parse(sql, **params)
        connection = sqlite3.connect(self.uri)
        cursor = connection.cursor()
        if args is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)

        records = cursor.fetchall()
        connection.close()

        columns, scalar, width = None, False, None
        objects = []
        for record in records:
            if columns is None:
                parts = list(record)
                desc = cursor.description
                if isinstance(desc[0], tuple) is True:
                    desc = [d[0] for d in desc]
                columns = []
                for x in xrange(len(parts)):
                    column = desc[x]
                    columns.append(column)
                width = len(columns)
                if width == 1:
                    scalar = True

            if scalar is True:
                for x in xrange(width):
                    value = record[x]
                    if isinstance(value, long) is True:
                        value = int(value)
                    objects.append(value)

            else:
                object = {}
                for x in xrange(width):
                    value = record[x]
                    column = columns[x]
                    object[column] = value

                objects.append(object)

        if adapter is not None:
            objects = map(adapter, objects)
        return objects

    @classmethod
    def open(cls, uri, constructor=None):
        return cls(uri, constructor=constructor)



class QueryBuffer(object):
    def __init__(self, db):
        self.db = db
        self.queries = []

    def append(self, sql, **params):
        if params.get("id", None) is None:
            if sql.find("@id") > -1:
                id = self.db.sequence()
                sql = sql.replace("@id", str(id))
                #params["id"] = self.db.sequence()

        sql, args = self.db.parse(sql, **params)
        self.queries.append((sql, args))
        return self

    def execute(self):
        queries = self.queries
        if len(queries) == 0:
            return

        connection = sqlite3.connect(self.db.uri)
        cursor = connection.cursor()
        for sql, args in queries:
            try:
                if args is None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, args)
            except Exception, ex:
                message = "Error executing statement: %s" % ex.message
                print message
                print sql

        connection.commit()
        self.queries = []
        return self

    def clear(self):
        self.queries = []
        return self

    def __len__(self):
        return len(self.queries)

    def __repr__(self):
        return "QueryByffer - %s queries" % str(len(self.queries))

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create(cls, db):
        return cls(db)