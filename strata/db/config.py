

class Config(object):
    def __init__(self, label=None, driver=None, uri=None, database=None,
                 username=None, password=None, port=None, pool_size=None, params=None):
        self.__label = label
        self.__driver = driver.strip().lower()
        self.__uri = uri if uri else "localhost"
        self.__database = database
        self.__username = username
        self.__password = password
        self.__port = port
        self.__pool_size = pool_size if pool_size and pool_size > 0 else 10
        self.__connection_string = None
        self.__params = {} if params is None else params


    @property
    def connection_string(self):
        txt = self.__connection_string
        if txt is not None:
            return txt

        driver = self.__driver
        if driver == "mysql":
            buffer = []
            buffer.append("%s://" % driver)
            if self.__username is not None:
                buffer.append("%s:%s@" % (self.__username, self.__password))
            buffer.append(self.__uri)
            if self.__database is not None:
                buffer.append("/%s" % self.__database)
            txt = "".join(buffer)
            self.__connection_string = txt
        else:
            raise Exception("The driver type is not recognized: %s" % driver)
        return self.__connection_string

    @property
    def params(self):
        return self.__params

    @property
    def driver(self):
        return self.__driver

    @property
    def uri(self):
        return self.__uri

    @property
    def database(self):
        return self.__database

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def port(self):
        return self.__port

    @property
    def pool_size(self):
        return self.__pool_size

    @property
    def label(self):
        label = self.__label
        if label is None:
            driver = self.driver
            server = self.server
            database = self.database
            label = "%s#%s@%s" % (driver, database, server)
            self.__label = label
        return label

    def deflate(self):
        return {
            "label": self.__label,
            "driver": self.__driver,
            "uri": self.__uri,
            "database": self.__database,
            "username": self.__username,
            "password": self.__password,
            "port": self.__port,
            "pool_size": self.__pool_size
        }

    @staticmethod
    def inflate(obj):
        return Config(
            label=obj["label"],
            driver=obj["driver"],
            uri=obj["uri"],
            database=obj["database"],
            username=obj["username"],
            password=obj["password"],
            port=obj["port"],
            pool_size=obj["pool_size"],
            )