from strata import util
from strata.db.query import Query


class QueryBatch(object):
    def __init__(self, db, auto_flush=None):
        self.db = db
        self.auto_flush = auto_flush
        self.queries = []


    def flush(self, force=False):
        queries = self.queries
        if len(queries) == 0:
            return
        self.queries = []
        if force is True:
            self.__process_queries__(queries, retries=0)
        else:
            self.__process_queries__(queries, retries=5)

    def clear(self):
        self.queries = []
        return self

    # def enable_auto_flush(self, query_count):
    #     self.auto_flush = query_count
    #     return self

    # def begin(self):
    #     inner = []
    #     self.queries.append(inner)
    #     self.inner = inner
    #     return self

        # if self.inside_block is True:
        #     self.queries.append("COMMIT;")
        #
        # self.inside_block = True
        # self.queries.append("START TRANSACTION;")

    def function(self, fn):
        self.queries.append(fn)

    def next(self, query, **kwd):
        return self.append(query, **kwd)

    def merge(self, queries):
        if len(queries.queries) > 0:
            self.queries.extend(queries.queries)
        return self

    def append(self, sql, **kwd):
        if isinstance(sql, QueryBatch) is True:
            if len(sql.queries) > 0:
                self.queries.extend(sql.queries)
            return self

        queries = self.queries# if self.inner is None else self.inner
        if util.is_function(sql) is True:
            queries.append(sql)
            return self

        if isinstance(sql, basestring) is True:
            if len(kwd) > 0:
                query = self.db.query(sql, **kwd)
                queries.append(query)
            else:
                query = self.db.query(sql)
                queries.append(query)
        else:
            query = sql
            if len(kwd) > 0:
                query.bind(kwd)
            queries.append(query)

        if self.auto_flush is not None and len(queries) >= self.auto_flush:
            self.execute()
        return self




    def execute(self, retries=None, callback=None, async=False):
        queries = self.queries
        if len(queries) == 0:
            return

        self.queries = []
        # if async is True:
        #     fn = tools.curry(self.process_queries, queries, callback=callback, retries=retries)
        #     tools.dispatch(fn)
        #     return

        self.__process_queries__(queries, callback=callback, retries=retries)


        # try:
        #     #o = self.db.transaction(self.queries, callback=callback)
        #     o = self.db.process_query_buffer(self.queries, callback=callback)
        #     self.queries = []
        #     return o
        # except Exception, ex:
        #     raise ex

    def __process_queries__(self, queries, callback=None, retries=None):
        if len(queries) == 0:
            return

        if retries is None:
            retries = 0

        while True:
            try:
                o = self.db.execute(queries)
                if callback is not None:
                    try:
                        callback(o)
                    except Exception, e:
                        message = "Error applying callback to results: %s" % e.message
                        print message
                return o
            except Exception, ex:
                if retries > 1:
                    retries = (retries - 1)
                    util.sleep(1)
                    continue
                raise ex

    # def load(self, queries):
    #     if isinstance(queries, basestring) is False:
    #         queries = queries.read_text()
    #     elif len(queries) <= 255 and queries.find("\n") == -1:
    #         if queries.find("/") > -1 or queries.find("\\") > -1:
    #             file = tools.file(queries)
    #             if file.exists is True:
    #                 queries = file.read_text()
    #     lines = queries.split("\n")
    #     for line in lines:
    #         line = line.strip()
    #         parts = line.split("\t")
    #         sql = parts[0].strip()
    #         if len(parts) == 1:
    #             if sql.strip().lower() == "begin":
    #                 self.begin()
    #             else:
    #                 self.append(sql)
    #         else:
    #             kwd = parts[1].strip()
    #             if kwd == "{}":
    #                 self.append(sql)
    #             else:
    #                 kwd = tools.unjson(kwd)
    #                 self.append(sql, **(kwd))
    #     return self


    # def export(self, uri):
    #     statement = self.stringify()
    #     file = tools.file(uri) if isinstance(uri, basestring) is True else uri
    #     file.write_text(statement, overwrite=True)
    #
    # def freeze(self):
    #     queries = self.queries
    #     def query_freeze(query):
    #         if isinstance(query, basestring) is True:
    #             return tools.base64(tools.pickle(query))
    #         return query.freeze()
    #
    #     queries = [query_freeze(query) for query in queries]
    #     object = {
    #         "database": self.db.id,
    #         "queries": queries
    #     }
    #     blob = tools.pickle(object)
    #     blob = tools.base64(blob)
    #     return blob
    #
    # def restore(self, blob):
    #     if blob.startswith("[") and blob.endswith("]"):
    #         return self.unpack(blob)
    #
    #     object = tools.unpickle(tools.unbase64(blob))
    #     queries = object.get("queries", None)
    #     if queries is None:
    #         return Query(db=self.db).restore(blob)
    #
    #     template = self.db.query("SELECT ID FROM member;")
    #     for x in xrange(len(queries)):
    #         query = queries[x]
    #         query = tools.unpickle(tools.unbase64(query))
    #         if isinstance(query, basestring) is False:
    #             query = template.restore(queries[x])
    #         queries[x] = query
    #
    #     return self
    #
    #     #for query in queries:
    #
    #
    #     #self.db.query(query
    #
    # def stringify(self):
    #     buffer = []
    #     def append_query(buffer, offset, query):
    #         if isinstance(query, list) is True:
    #             if len(query) > 0:
    #                 if offset == 0:
    #                     buffer.append("BEGIN")
    #                 else:
    #                     padding = ("\t" * offset)
    #                     buffer.append("{padding}BEGIN".format(padding=padding))
    #                 offset = (offset + 1)
    #                 for q in query:
    #                     append_query(offset, q)
    #             return
    #
    #         if isinstance(query, basestring) is True:
    #             while query.find("\n") > -1:
    #                 query = query.replace("\n", " ")
    #             while query.find("\r") > -1:
    #                 query = query.replace("\r", " ")
    #             while query.find("\t") > -1:
    #                 query = query.replace("\t", " ")
    #             while query.find("  ") > -1:
    #                 query = query.replace("  ", " ")
    #             if offset > 0:
    #                 padding = ("\t" * offset)
    #                 buffer.append("{padding}{query}".format(padding=padding, query=query))
    #             else:
    #                 buffer.append(query)
    #         elif tools.not_blank(query):
    #             query = query.stringify()
    #             if offset > 0:
    #                 padding = ("\t" * offset)
    #                 buffer.append("{padding}{query}".format(padding=padding, query=query))
    #             else:
    #                 buffer.append(query)
    #
    #     append_query = util.curry(append_query, buffer)
    #     for query in self.queries:
    #         append_query(0, query)
    #     txt = "\n".join(buffer)
    #     return txt

    #
    # def inline(self):
    #     buffer = []
    #     def append_query(buffer, offset, query):
    #         if isinstance(query, list) is True:
    #             if len(query) > 0:
    #                 if offset == 0:
    #                     buffer.append("BEGIN")
    #                 else:
    #                     padding = ("\t" * offset)
    #                     buffer.append("{padding}BEGIN".format(padding=padding))
    #                 offset = (offset + 1)
    #                 for q in query:
    #                     append_query(offset, q)
    #             return
    #
    #         if isinstance(query, basestring) is True:
    #             while query.find("\n") > -1:
    #                 query = query.replace("\n", " ")
    #             while query.find("\r") > -1:
    #                 query = query.replace("\r", " ")
    #             while query.find("\t") > -1:
    #                 query = query.replace("\t", " ")
    #             while query.find("  ") > -1:
    #                 query = query.replace("  ", " ")
    #             if offset > 0:
    #                 padding = ("\t" * offset)
    #                 buffer.append("{padding}{query}".format(padding=padding, query=query))
    #             else:
    #                 buffer.append(query)
    #         elif tools.not_blank(query):
    #             query = query.inline()
    #             if offset > 0:
    #                 padding = ("\t" * offset)
    #                 buffer.append("{padding}{query}".format(padding=padding, query=query))
    #             else:
    #                 buffer.append(query)
    #
    #     append_query = tools.curry(append_query, buffer)
    #     for query in self.queries:
    #         append_query(0, query)
    #     txt = "\n".join(buffer)
    #     return txt


    # def pack(self):
    #     txt = self.stringify()
    #     txt = tools.base64(tools.compress(txt))
    #     txt = "[QueryBuffer:%s]" % txt
    #     return txt
    #
    # def unpack(self, txt):
    #     parts = txt.split(":")
    #     parts = parts[1:]
    #     txt = ":".join(parts)
    #     txt = txt[0:len(txt) - 1]
    #
    #     #txt = parts[1].strip()
    #     txt = tools.decompress(tools.unbase64(txt))
    #     lines = txt.split("\n")
    #     for line in lines:
    #         parts = line.split("\t")
    #         sql = parts[0]
    #         if len(parts) == 1:
    #             self.append(sql)
    #             continue
    #         params = "\t".join(parts[1:])
    #         params = tools.unjson(params)
    #         self.append(sql, **(params))
    #
    #     return self


    def __iter__(self):
        return self.next()

    def next(self):
        def iterate(queries):
            for query in queries:
                if isinstance(query, list) is True:
                    yield iterate(query)
                else:
                    yield query

        queries = self.queries
        for query in iterate(queries):
            yield query

    @property
    def count(self):
        return len(self.queries)

    @property
    def empty(self):
        return True if len(self.queries) == 0 else False

    @classmethod
    def create(cls, db):
        return cls(db)

    def __len__(self):
        return len(self.queries)

    def __repr__(self):
        return "QueryBatch - %s queries" % str(len(self.queries))

    def __str__(self):
        return self.__repr__()

