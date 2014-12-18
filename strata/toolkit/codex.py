from .crypto import *



class Codex(object):
    __slots__ = [
        "__salt__",
        "__weak__",
        "__strong__",
        "__hmac__"
    ]

    def __init__(self, salt=None, strong=None, weak=None, hmac=None):
        self.__salt__ = salt
        self.__strong__ = strong
        self.__weak__ = weak
        self.__hmac__ = hmac


    def encrypt(self, data):
        from .. import toolkit

        key = self.__weak__
        data = toolkit.aes.encrypt(key, data)
        data = toolkit.base64(data)
        return data

    def decrypt(self, data):
        from .. import toolkit

        key = self.__weak__
        data = toolkit.unbase64(data)
        data = toolkit.aes.decrypt(key, data)
        return data


    def seal(self, *args, **kwd):
        if not kwd:
            if len(args) == 0:
                raise Exception("The parameter is null!")
            kwd = args[0]

        from .. import toolkit

        object = {}
        for key in kwd.keys():
            object[key] = kwd[key]

        key = self.__weak__
        data = toolkit.pickle(object)
        data = toolkit.aes.encrypt(key, data)
        data = toolkit.base64(data)
        digest = toolkit.digest(self.__hmac__, data)
        digest = toolkit.base64(digest)

        cnt = len(digest)
        prefix = str(cnt)
        if len(prefix) == 1:
            prefix = "00%s" % prefix
        elif len(prefix) == 2:
            prefix = "0%s" % prefix

        buffer = []
        buffer.append(prefix)
        buffer.append(digest)
        buffer.append(data)
        data = "".join(buffer)
        return data

    def unseal(self, data):
        from .. import toolkit

        prefix = data[:3]
        if prefix.startswith("00") is True:
            prefix = prefix[2:]
        elif prefix.startswith("0") is True:
            prefix = prefix[1:]
        cnt = int(prefix)
        offset = (3 + cnt)
        digest = data[3:cnt]


        data = data[offset:]

        verify = toolkit.digest(self.__hmac__, data)
        verify = toolkit.base64(verify)

        if verify.startswith(digest) is False:
            raise Exception("The message digest is invalid, maybe tampered with.")

        key = self.__weak__
        data = toolkit.unbase64(data)
        data = toolkit.aes.decrypt(key, data)
        object = toolkit.unpickle(data)
        return object


    def clone(self):
        return Codex(
            salt=self.__salt__,
            strong=self.__strong__,
            weak=self.__weak__,
            hmac=self.__hmac__
        )

    def __repr__(self):
        return "Codex"
