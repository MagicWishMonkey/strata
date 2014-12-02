import socket


class SocketServlet(object):
    def __init__(self, port, host="", backlog=10, chunk_size=4096):
        self.port = port
        self.host = host
        self.backlog = backlog
        self.chunk_size = chunk_size
        self.__socket__ = None
        self.__worker__ = None

    def start(self, callback, async=False):
        if self.__socket__ is not None:
            return self

        if async is True:
            from strata import util
            fn = util.curry(self.start, callback)
            self.__worker__ = util.dispatch(fn)
            return self

        from strata import util
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(self.backlog)
        self.__socket__ = s
        chunk_size = self.chunk_size
        while self.__socket__ is not None:
            client, address = s.accept()
            data = client.recv(chunk_size)
            if data is not None:
                try:
                    response = callback(data)
                    if response is not None:
                        #util.sleep(.1)
                        client.send(response)
                    else:
                        client.send("")
                except Exception, ex:
                    message = "Error with client callback: %s" % ex.message
                    print message

            client.close()


    def stop(self):
        if self.__socket__ is None:
            return self
        try:
            self.__socket__.close()
        except:
            pass

        self.__socket__ = None
        if self.__worker__ is not None:
            try:
                print "Aborting worker"
                self.__worker__.join()
                print "Aborted..."
            except:
                pass
            self.__worker__ = None

        return self


    def chat(self, txt):
        host = self.host
        if host is None or len(host) == 0:
            host = socket.gethostname()
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, self.port))
            client.send(txt)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except Exception, ex:
            message = "Error sending message: %s" % ex.message
            print message
