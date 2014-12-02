import threading


thread_local_storage = threading.local()


def set(key, val):
    try:
        if val is not None:
            setattr(thread_local_storage, key, val)
        return val
    except:
        return None


def get(key):
    try:
        ctx = getattr(thread_local_storage, key, None)
        return ctx
    except:
        return None


def clear(key):
    try:
        val = getattr(thread_local_storage, key, None)
        if val is None:
            return

        #val.clear()
    except:
        pass

    try:
        setattr(thread_local_storage, key, None)
    except:
        pass
