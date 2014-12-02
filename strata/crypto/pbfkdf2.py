import os
import sys
import hmac
import hashlib
from operator import xor
from itertools import izip, starmap
from struct import Struct



class PasswordGenerator:
    """
    A PBKDF2 password hashing algorithm borrowed from
    https://github.com/mitsuhiko/python-pbkdf2.

    """
    __KEYLEN__ = 24
    __ITERATIONS__ = 1500
    __HASH_FUNC__ = hashlib.sha512
    __PACK_INT__ = Struct('>I').pack


    @staticmethod
    def generate(input, salt, iterations=None, keylen=None, hash_func=None):
        assert isinstance(input, basestring), "The input parameter is not a valid string!"
        assert isinstance(salt, basestring), "The input parameter is not a valid string!"

        if iterations is None:
            iterations = PasswordGenerator.__ITERATIONS__
        if keylen is None:
            keylen = PasswordGenerator.__KEYLEN__
        if hash_func is None:
            hash_func = PasswordGenerator.__HASH_FUNC__

        mac = hmac.new(input, None, hash_func)
        def _pseudorandom(x, mac=mac):
            h = mac.copy()
            h.update(x)
            return map(ord, h.digest())
        buf = []
        for block in xrange(1, -(-keylen // mac.digest_size) + 1):
            rv = u = _pseudorandom(salt + PasswordGenerator.__PACK_INT__(block))
            for i in xrange(iterations - 1):
                u = _pseudorandom(''.join(map(chr, u)))
                rv = starmap(xor, izip(rv, u))
            buf.extend(rv)
        txt = ''.join(map(chr, buf))[:keylen]
        return txt.encode('hex')

    @staticmethod
    def check(data, salt, expected, iterations=None, keylen=None, hash_func=None):
        actual = PasswordGenerator.generate(data, salt, iterations=iterations, keylen=keylen, hash_func=hash_func)
        if actual != expected:
            return False
        return True

    @staticmethod
    def test():
        failed = []
        def check(data, salt, iterations, keylen, expected):
            rv = PasswordGenerator.generate(data, salt, iterations=iterations, keylen=keylen)
            print rv
            if rv != expected:
                print 'Test failed:'
                print '  Expected:   %s' % expected
                print '  Got:        %s' % rv
                print '  Parameters:'
                print '    data=%s' % data
                print '    salt=%s' % salt
                print '    iterations=%d' % iterations
                print
                failed.append(1)

        # From RFC 6070
        check('password', 'salt', 1, 20, '867f70cf1ade02cff3752599a3a53dc4af34c7a6')
        check('password', 'salt', 2, 20, 'e1d9c16aa681708a45f5c7c4e215ceb66e011a2e')
        check('password', 'salt', 4096, 20, 'd197b1b33db0143e018b12f3d1d1479e6cdebdcc')
        check('passwordPASSWORDpassword', 'saltSALTsaltSALTsaltSALTsaltSALTsalt', 4096, 25, '8c0511f4c6e597c6ac6315d8f0362e225f3c501495ba23b868')
        check('pass\x00word', 'sa\x00lt', 4096, 16, '9d9e9c4cd21fe4be24d5b8244c759665')
        # This one is from the RFC but it just takes for ages
        #check('password', 'salt', 16777216, 20, 'eefe3d61cd4da4e4e9945b3d6ba2158c2634e984')

        # From Crypt-PBKDF2
        check('password', 'ATHENA.MIT.EDUraeburn', 1, 16, 'bd895e42b0f12eb9ccaa3c19368164a8')
        check('password', 'ATHENA.MIT.EDUraeburn', 1, 32, 'bd895e42b0f12eb9ccaa3c19368164a83e34f9e2cf31d621d919a74629fbdae0')
        check('password', 'ATHENA.MIT.EDUraeburn', 2, 16, '59f72373fb5573d1b95e07f822ffac82')
        check('password', 'ATHENA.MIT.EDUraeburn', 2, 32, '59f72373fb5573d1b95e07f822ffac82b95aec3f8099c943eeaeb3045bffbdc1')
        check('password', 'ATHENA.MIT.EDUraeburn', 1200, 32, 'fa34d048bd2e97fc93251076a876408afb2db1d1c51646d7597acf1d7cab7159')
        check('X' * 64, 'pass phrase equals block size', 1200, 32, 'dbdddd4eaefc554a4459ac808fa6c152c7ea483febcedb7cc2890eae30dc64fe')
        check('X' * 65, 'pass phrase exceeds block size', 1200, 32, '6134b62e41b2adc8e224256b9c69831fa630aa3b72626a6d5d141d18f20d142d')
