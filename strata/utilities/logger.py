

class Logger(object):
    __instance__ = None
    def __init__(self):
        if Logger.__instance__ is None:
            Logger.__instance__ = self

        self.enabled = False

    # def debug(*message, **kwd):
    #     pass
    #
    # def __debug__(*message, **kwd):
    #     pass

    def trace(*message, **kwd):
        pass

    def __trace__(*message, **kwd):
        pass

    def info(*message, **kwd):
        pass

    def __info__(*message, **kwd):
        pass


    @staticmethod
    def activate():
        Logger()

    @staticmethod
    def get():
        return Logger.__instance__


if Logger.__instance__ is None:
    Logger.activate()
