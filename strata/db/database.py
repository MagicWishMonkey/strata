from .config import Config
from .query import Query
from .query_batch import QueryBatch
from .error import *
from .. import toolkit
from sqlalchemy import text
from sqlalchemy import create_engine



class Database(object):
    __slots__ = [
        "config",
        "__engine"
    ]

    def __init__(self, config):
        self.config = config
        self.__engine = None

    @property
    def label(self):
        return self.config.label
        # driver = self.config.driver
        # server = self.config.server
        # database = self.config.database
        # label = "%s#%s@%s" % (driver, database, server)
        # return label

    @property
    def engine(self):
        engine = self.__engine
        if engine is not None:
            return engine

        conn_str = self.config.connection_string
        params = self.config.params
        engine = None
        if len(params) == 0:
            engine = create_engine(conn_str)
        else:
            engine = create_engine(conn_str, **(params))

        self.__engine = engine
        return engine

    def clone(self):
        return Database(self.config)

    # def __execute(self, query, select=False, stream=None):
    #     assert query is not None, "The query parameter is null!"
    #     queries = tools.prepare_query(query)
    #     single = True if isinstance(queries, list) is False else False
    #     if single is True:
    #         queries = [queries]
    #
    #
    #     cnt = len(queries)
    #     connection, transaction = None, None
    #     try:
    #         connection = self.engine.connect()
    #     except Exception, ex:
    #         msg = "Could not connect to the database-> %s" % ex.message
    #         raise DatabaseError(msg, ex)
    #
    #     if select is False:
    #         try:
    #             transaction = connection.begin()
    #         except Exception, ex:
    #             try:
    #                 connection.close()
    #             except:
    #                 pass
    #             msg = "Could creating the transaction object-> %s" % ex.message
    #             raise DatabaseError(msg, ex)
    #
    #     try:
    #         query, sql, params = None, None, None
    #         results = []
    #         for x in xrange(cnt):
    #             query = queries[x]
    #             sql, params = query["sql"], query["params"]
    #             try:
    #                 if params is None:
    #                     result = connection.execute(text(sql))
    #                     if result is not None:
    #                         if select is True:
    #                             if stream is not None:
    #                                 stream(result)
    #                             else:
    #                                 result = tools.extract_recordset(result)
    #                         elif result.lastrowid is not None:
    #                             result = int(result.lastrowid)
    #                     else:
    #                         result = [] #the result record is null
    #                     results.append(result)
    #                 else:
    #                     result = connection.execute(text(sql), params)
    #                     if result is not None:
    #                         if select is True:
    #                             if stream is not None:
    #                                 stream(result)
    #                             else:
    #                                 result = tools.extract_recordset(result)
    #
    #                         elif result.lastrowid is not None:
    #                             result = int(result.lastrowid)
    #                     else:
    #                         result = []#the result record is null
    #                     results.append(result)
    #             except Exception, e:
    #                 raise DatabaseQueryError(
    #                     e,
    #                     db=self,
    #                     query=query
    #                 )
    #
    #         if transaction is not None:
    #             transaction.commit()
    #
    #         if single is True:
    #             return results[0] if len(results) > 0 else None
    #         return results
    #     except Exception, ex:
    #         if transaction is not None:
    #             try:
    #                 transaction.rollback()
    #             except:
    #                 pass
    #         if isinstance(ex, FuzeError) is False:
    #             raise DatabaseQueryError(
    #                 e,
    #                 db=self,
    #                 query=query
    #             )
    #         raise ex
    #     finally:
    #         try:
    #             if self.engine != connection:
    #                 connection.close()
    #         except Exception, ex:
    #             message = ex.message
    #             try:
    #                 code, message = ex.args[0], ex.args[1]
    #             except:
    #                 pass
    #
    #             msg = "Could not close the database connection-> %s" % message
    #             ex = DatabaseError(msg, ex)
    #             logger.error(ex)


    def enter(self, use_txn=False):
        return Connection(self, use_txn=use_txn)

    def select(self, sql, **params):
        with self.enter(use_txn=False) as conn:
            return conn.select(sql, **params)

    def insert(self, sql, **params):
        with self.enter(use_txn=True) as conn:
            return conn.execute(sql, **params)

    def update(self, sql, **params):
        with self.enter(use_txn=True) as conn:
            return conn.execute(sql, **params)

    def delete(self, sql, **params):
        with self.enter(use_txn=True) as conn:
            return conn.execute(sql, **params)

    def execute(self, sql, **params):
        with self.enter(use_txn=True) as conn:
            return conn.execute(sql, **params)

    def query_buffer(self):
        return QueryBatch.create(self)


    def query(self, *args, **params):
        sql = args[0]

        allow_cache = False
        sql = sql.strip()
        if sql.find(" ") == -1:
            #this is a file based query
            allow_cache = True
        elif sql.find("@") > -1:
            allow_cache = True

        key = None
        if allow_cache is True:
            key = toolkit.hash(sql)
            # print "TODO: add cache table for fetching queries!"

        qry = Query.create(sql)
        if allow_cache is True:
            qry.key = key
            # print "TODO: add cache table for saving queries!"

        if len(args) > 1:
            qry.bind(args[1])
        elif len(params) > 0:
            qry.bind(params)

        qry.set_db(self)
        return qry


    @classmethod
    def plugin(cls, plugin):
        setattr(cls, plugin.func_name, plugin)

    @classmethod
    def open(cls, **kwd):
        driver = kwd.get("driver", None)
        if driver is None:
            raise DatabaseError("The database driver is not specified.")

        params = kwd.get("params", {})
        config = Config(
            driver=driver,
            label=kwd.get("label", None),
            uri=kwd.get("uri", None),
            database=kwd.get("database", None),
            username=kwd.get("username", None),
            password=kwd.get("password", None),
            port=kwd.get("port", None),
            pool_size=kwd.get("pool_size", None),
            params=params
        )
        return cls(config)

    def __str__(self):
        return self.label

    def __repr__(self):
        return self.__repr__()

    @classmethod
    def create(cls, db):
        return cls(db)




class Connection(object):
    __slots__ = ["__db__", "__conn__", "__txn__", "__qry__", "use_txn"]
    def __init__(self, db, use_txn=False):
        self.__db__ = db
        self.__conn__ = None
        self.__txn__ = None
        self.__qry__ = None, None
        self.use_txn = use_txn

    def __enter__(self):
        self.__conn__ = self.__db__.engine.connect()
        if self.use_txn is True:
            self.__txn__ = self.__conn__.begin()
        return self

    def __exit__(self, error_type, error_val, error_tb):
        conn = self.__conn__
        txn = self.__txn__
        if txn is not None:
            if error_val is None:
                try:
                    txn.commit()
                except:
                    pass
            else:
                try:
                    txn.rollback()
                except:
                    pass
            self.__txn__ = None

        if conn is not None:
            try:
                conn.close()
            except:
                pass
            self.__conn__ = None

        if error_val is not None:
            sql, params = None, None
            try:
                sql = self.__qry__[0]
            except:
                pass

            try:
                params = self.__qry__[1]
            except:
                pass

            self.__qry__ = None, None

            type = error_type.__name__
            message = error_val.message

            if sql is None:
                try:
                    sql = error_val.statement
                except:
                    pass

            if params is None:
                try:
                    params = error_val.params
                except:
                    pass

                if params is not None:
                    if len(params) == 0:
                        params = None
                    else:
                        obj = {}
                        for x, param in enumerate(params):
                            obj[x] = param
                        params = obj
            if sql is None:
                raise DatabaseError(message, inner=error_val)
            raise DatabaseQueryError(message, sql=sql, params=params, inner=error_val)
        self.__qry__ = None, None

    def select(self, sql, **params):
        return self.execute(sql, **params)

    def execute(self, sql, **params):
        self.__qry__ = None, None

        if isinstance(sql, basestring) is False:
            if isinstance(sql, list) is True:
                queries = sql
                if len(queries) == 0:
                    return None

                if self.__txn__ is None:
                    self.use_txn = True
                    self.__txn__ = self.__conn__.begin()

                return map(self.execute, queries)
            elif isinstance(sql, Query) is True:
                qry = sql
                sql = qry.sql
                params = qry.params
                if params is None:
                    params = {}

        conn = self.__conn__

        self.__qry__ = (sql, None) if len(params) == 0 else (sql, params)

        sql = text(sql)
        result, records = None, None
        if len(params) == 0:
            result = conn.execute(sql)
        else:
            result = conn.execute(sql, **params)

        if result is not None:
            if result.lastrowid is not None and result.lastrowid > 0:
                records = int(result.lastrowid)
            elif result.returns_rows is True:
                records = Connection.extract_recordset(result)
        return records

    @staticmethod
    def extract_recordset(records):
        columns = None
        objects = []
        adapters = []
        count = -1
        scalar = False
        for record in records:
            if count == -1:
                columns = record.keys()
                count = len(columns)
                adapters = [None for x in xrange(count)]
                for x in xrange(count):
                    column = columns[x]
                    value = record[column]
                    if isinstance(value, long) is True:
                        adapters[x] = lambda x: int(x)
                if count == 1:
                    scalar = True

            if scalar is True:
                for x in xrange(count):
                    column = columns[x]
                    value = record[column]

                    adapter = adapters[x]
                    if adapter is not None:
                        try:
                            value = adapter(value)
                        except:
                            pass
                    objects.append(value)
            else:
                object = {}
                for x in xrange(count):
                    column = columns[x]
                    value = record[column]

                    adapter = adapters[x]
                    if adapter is not None:
                        try:
                            value = adapter(value)
                        except:
                            pass
                    object[column] = value
                objects.append(object)
        return objects