import subprocess


class __Shell__(object):
    def __init__(self):
        pass

    @staticmethod
    def invoke(target, *args):
        command = []
        command.append(target)
        for arg in args:
            command.append(arg)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()
        if stderr:
            return stderr

        buffer = []
        lines = stdout.split("\n")
        for line in lines:
            if len(line) > 0:
                buffer.append(line)

        txt = "\n".join(buffer)
        return txt

    def __getattr__(self, method):
        def curry(f, *a, **kw):
            def curried(*more_a, **more_kw):
                return f(*(a + more_a), **dict(kw, **more_kw))
            return curried

        fn = curry(__Shell__.invoke, method)
        return fn

shell = __Shell__()
