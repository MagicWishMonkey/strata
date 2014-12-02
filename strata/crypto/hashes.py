import hashlib




def md5(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.md5(data).hexdigest()
    except Exception, ex:
        try:
            data = data.encode('ascii', 'ignore')
            hashed = hashlib.md5(data).hexdigest()
            return hashed
        except:
            message = "Error creating md5 hash-> %s" % ex.message
            raise Exception(message, ex)


def sha1(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.sha1(data).hexdigest()
    except Exception, ex:
        try:
            data = data.encode('ascii', 'ignore')
            hashed = hashlib.md5(data).hexdigest()
            return hashed
        except:
            message = "Error creating sha1 hash-> %s" % ex.message
            raise Exception(message, ex)



def sha224(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.sha224(data).hexdigest()
    except Exception, ex:
        try:
            data = data.encode('ascii', 'ignore')
            hashed = hashlib.md5(data).hexdigest()
            return hashed
        except:
            message = "Error creating sha224 hash-> %s" % ex.message
            raise Exception(message, ex)



def sha256(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.sha256(data).hexdigest()
    except Exception, ex:
        message = "Error creating sha256 hash-> %s" % ex.message
        raise Exception(message, ex)



def sha384(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.sha384(data).hexdigest()
    except Exception, ex:
        try:
            data = data.encode('ascii', 'ignore')
            hashed = hashlib.md5(data).hexdigest()
            return hashed
        except:
            message = "Error creating sha384 hash-> %s" % ex.message
            raise Exception(message, ex)



def sha512(data):
    assert data is not None, "The input data is null!"

    try:
        data = data if isinstance(data, basestring) else str(data)
        return hashlib.sha512(data).hexdigest()
    except Exception, ex:
        try:
            data = data.encode('ascii', 'ignore')
            hashed = hashlib.md5(data).hexdigest()
            return hashed
        except:
            message = "Error creating sha512 hash-> %s" % ex.message
            raise Exception(message, ex)