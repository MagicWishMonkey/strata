# -*- coding: utf-8 -*-
from __future__ import with_statement
import codecs
from operator import itemgetter
import re
import urlparse


SCHEME_RE = re.compile(r'^([' + urlparse.scheme_chars + ']+:)?//')
IP_RE = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')


class ExtractResult(tuple):
    'ExtractResult(subdomain, domain, tld)'
    __slots__ = ()
    _fields = ('subdomain', 'domain', 'tld')

    def __new__(_cls, subdomain, domain, tld):
        'Create new instance of ExtractResult(subdomain, domain, tld)'
        return tuple.__new__(_cls, (subdomain, domain, tld))

    @classmethod
    def _make(cls, iterable, new=tuple.__new__, len=len):
        'Make a new ExtractResult object from a sequence or iterable'
        result = new(cls, iterable)
        if len(result) != 3:
            raise TypeError('Expected 3 arguments, got %d' % len(result))
        return result

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'ExtractResult(subdomain=%r, domain=%r, tld=%r)' % self

    def _asdict(self):
        'Return a new dict which maps field names to their values'
        return dict(zip(self._fields, self))

    def _replace(_self, **kwds):
        'Return a new ExtractResult object replacing specified fields with new values'
        result = _self._make(map(kwds.pop, ('subdomain', 'domain', 'tld'), _self))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % kwds.keys())
        return result

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    subdomain = property(itemgetter(0), doc='Alias for field number 0')
    domain = property(itemgetter(1), doc='Alias for field number 1')
    tld = property(itemgetter(2), doc='Alias for field number 2')


def extract(url):
    """
    Takes a string URL and splits it into its subdomain, domain, and
    gTLD/ccTLD component. Ignores scheme, username, and path components.

    >>> extract('http://forums.news.cnn.com/')
    ExtractResult(subdomain='forums.news', domain='cnn', tld='com')
    >>> extract('http://forums.bbc.co.uk/')
    ExtractResult(subdomain='forums', domain='bbc', tld='co.uk')
    """
    netloc = SCHEME_RE.sub("", url).partition("/")[0]
    return _extract(netloc)


def urlsplit(url):
    """Same as `extract` but calls urlparse.urlsplit to further 'validate' the
    input URL. This function will therefore raise the same errors as
    urlparse.urlsplit and handle some inputs differently than extract, such as
    URLs missing a scheme.

    >>> urlsplit('http://forums.news.cnn.com/')
    ExtractResult(subdomain='forums.news', domain='cnn', tld='com')
    >>> urlsplit('forums.bbc.co.uk/') # urlsplit won't see a netloc
    ExtractResult(subdomain='', domain='', tld='')
    """
    netloc = urlparse.urlsplit(url).netloc
    return _extract(netloc)

def _extract(netloc):
    netloc = netloc.split("@")[-1].partition(':')[0]
    registered_domain, tld = netloc, ''
    m = _get_extract_tld_re().match(netloc)
    if m:
        registered_domain, tld = m.group('registered_domain'), m.group('tld')
    else:
        return ExtractResult("", "", "")

    subdomain, _, domain = registered_domain.rpartition('.')
    return ExtractResult(subdomain, domain, tld)

EXTRACT_TLD_RE_RAW = ''
EXTRACT_TLD_RE = None

def _get_extract_tld_re():
    global EXTRACT_TLD_RE, EXTRACT_TLD_RE_RAW
    if EXTRACT_TLD_RE:
        return EXTRACT_TLD_RE

    pattern = "^(?P<registered_domain>.+?)\.(?P<tld>aero|arpa|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|post|pro|tel|travel|测试|परीक्षा|한국|ভারত|বাংলা|испытание|қаз|срб|테스트|சிங்கப்பூர்|טעסט|中国|中國|భారత్|ලංකා|測試|ભારત|भारत|آزمایشی|பரிட்சை|укр|香港|δοκιμή|إختبار|台湾|台灣|мон|الجزائر|عمان|ایران|امارات|پاکستان|الاردن|بھارت|المغرب|السعودية|سودان|مليسيا|გე|ไทย|سورية|рф|تونس|ਭਾਰਤ|مصر|قطر|இலங்கை|இந்தியா|新加坡|فلسطين|テスト|xxx|co\.ad|org\.ad|ac\.ad|ad|co\.ae|org\.ae|ac\.ae|ae|co\.af|org\.af|ac\.af|af|co\.ag|org\.ag|ac\.ag|ag|co\.ai|org\.ai|ac\.ai|ai|co\.al|org\.al|ac\.al|al|co\.am|org\.am|ac\.am|am|co\.an|org\.an|ac\.an|an|co\.ao|org\.ao|ac\.ao|ao|co\.aq|org\.aq|ac\.aq|aq|co\.ar|org\.ar|ac\.ar|ar|co\.as|org\.as|ac\.as|as|co\.at|org\.at|ac\.at|at|co\.au|org\.au|ac\.au|au|co\.aw|org\.aw|ac\.aw|aw|co\.ax|org\.ax|ac\.ax|ax|co\.az|org\.az|ac\.az|az|co\.ba|org\.ba|ac\.ba|ba|co\.bb|org\.bb|ac\.bb|bb|co\.bd|org\.bd|ac\.bd|bd|co\.be|org\.be|ac\.be|be|co\.bf|org\.bf|ac\.bf|bf|co\.bg|org\.bg|ac\.bg|bg|co\.bh|org\.bh|ac\.bh|bh|co\.bi|org\.bi|ac\.bi|bi|co\.bj|org\.bj|ac\.bj|bj|co\.bl|org\.bl|ac\.bl|bl|co\.bm|org\.bm|ac\.bm|bm|co\.bn|org\.bn|ac\.bn|bn|co\.bo|org\.bo|ac\.bo|bo|co\.bq|org\.bq|ac\.bq|bq|co\.br|org\.br|ac\.br|br|co\.bs|org\.bs|ac\.bs|bs|co\.bt|org\.bt|ac\.bt|bt|co\.bv|org\.bv|ac\.bv|bv|co\.bw|org\.bw|ac\.bw|bw|co\.by|org\.by|ac\.by|by|co\.bz|org\.bz|ac\.bz|bz|co\.ca|org\.ca|ac\.ca|ca|co\.cc|org\.cc|ac\.cc|cc|co\.cd|org\.cd|ac\.cd|cd|co\.cf|org\.cf|ac\.cf|cf|co\.cg|org\.cg|ac\.cg|cg|co\.ch|org\.ch|ac\.ch|ch|co\.ci|org\.ci|ac\.ci|ci|co\.ck|org\.ck|ac\.ck|ck|co\.cl|org\.cl|ac\.cl|cl|co\.cm|org\.cm|ac\.cm|cm|co\.cn|org\.cn|ac\.cn|cn|co\.cr|org\.cr|ac\.cr|cr|co\.cu|org\.cu|ac\.cu|cu|co\.cv|org\.cv|ac\.cv|cv|co\.cw|org\.cw|ac\.cw|cw|co\.cx|org\.cx|ac\.cx|cx|co\.cy|org\.cy|ac\.cy|cy|co\.cz|org\.cz|ac\.cz|cz|co\.de|org\.de|ac\.de|de|co\.dj|org\.dj|ac\.dj|dj|co\.dk|org\.dk|ac\.dk|dk|co\.dm|org\.dm|ac\.dm|dm|co\.do|org\.do|ac\.do|do|co\.dz|org\.dz|ac\.dz|dz|co\.ec|org\.ec|ac\.ec|ec|co\.ee|org\.ee|ac\.ee|ee|co\.eg|org\.eg|ac\.eg|eg|co\.eh|org\.eh|ac\.eh|eh|co\.er|org\.er|ac\.er|er|co\.es|org\.es|ac\.es|es|co\.et|org\.et|ac\.et|et|co\.eu|org\.eu|ac\.eu|eu|co\.fi|org\.fi|ac\.fi|fi|co\.fj|org\.fj|ac\.fj|fj|co\.fk|org\.fk|ac\.fk|fk|co\.fm|org\.fm|ac\.fm|fm|co\.fo|org\.fo|ac\.fo|fo|co\.fr|org\.fr|ac\.fr|fr|co\.ga|org\.ga|ac\.ga|ga|co\.gb|org\.gb|ac\.gb|gb|co\.gd|org\.gd|ac\.gd|gd|co\.ge|org\.ge|ac\.ge|ge|co\.gf|org\.gf|ac\.gf|gf|co\.gg|org\.gg|ac\.gg|gg|co\.gh|org\.gh|ac\.gh|gh|co\.gi|org\.gi|ac\.gi|gi|co\.gl|org\.gl|ac\.gl|gl|co\.gm|org\.gm|ac\.gm|gm|co\.gn|org\.gn|ac\.gn|gn|co\.gp|org\.gp|ac\.gp|gp|co\.gq|org\.gq|ac\.gq|gq|co\.gr|org\.gr|ac\.gr|gr|co\.gs|org\.gs|ac\.gs|gs|co\.gt|org\.gt|ac\.gt|gt|co\.gu|org\.gu|ac\.gu|gu|co\.gw|org\.gw|ac\.gw|gw|co\.gy|org\.gy|ac\.gy|gy|co\.hk|org\.hk|ac\.hk|hk|co\.hm|org\.hm|ac\.hm|hm|co\.hn|org\.hn|ac\.hn|hn|co\.hr|org\.hr|ac\.hr|hr|co\.ht|org\.ht|ac\.ht|ht|co\.hu|org\.hu|ac\.hu|hu|co\.id|org\.id|ac\.id|id|co\.ie|org\.ie|ac\.ie|ie|co\.il|org\.il|ac\.il|il|co\.im|org\.im|ac\.im|im|co\.in|org\.in|ac\.in|in|co\.io|org\.io|ac\.io|io|co\.iq|org\.iq|ac\.iq|iq|co\.ir|org\.ir|ac\.ir|ir|co\.is|org\.is|ac\.is|is|co\.it|org\.it|ac\.it|it|co\.je|org\.je|ac\.je|je|co\.jm|org\.jm|ac\.jm|jm|co\.jo|org\.jo|ac\.jo|jo|co\.jp|org\.jp|ac\.jp|jp|co\.ke|org\.ke|ac\.ke|ke|co\.kg|org\.kg|ac\.kg|kg|co\.kh|org\.kh|ac\.kh|kh|co\.ki|org\.ki|ac\.ki|ki|co\.km|org\.km|ac\.km|km|co\.kn|org\.kn|ac\.kn|kn|co\.kp|org\.kp|ac\.kp|kp|co\.kr|org\.kr|ac\.kr|kr|co\.kw|org\.kw|ac\.kw|kw|co\.ky|org\.ky|ac\.ky|ky|co\.kz|org\.kz|ac\.kz|kz|co\.la|org\.la|ac\.la|la|co\.lb|org\.lb|ac\.lb|lb|co\.lc|org\.lc|ac\.lc|lc|co\.li|org\.li|ac\.li|li|co\.lk|org\.lk|ac\.lk|lk|co\.lr|org\.lr|ac\.lr|lr|co\.ls|org\.ls|ac\.ls|ls|co\.lt|org\.lt|ac\.lt|lt|co\.lu|org\.lu|ac\.lu|lu|co\.lv|org\.lv|ac\.lv|lv|co\.ly|org\.ly|ac\.ly|ly|co\.ma|org\.ma|ac\.ma|ma|co\.mc|org\.mc|ac\.mc|mc|co\.md|org\.md|ac\.md|md|co\.me|org\.me|ac\.me|me|co\.mf|org\.mf|ac\.mf|mf|co\.mg|org\.mg|ac\.mg|mg|co\.mh|org\.mh|ac\.mh|mh|co\.mk|org\.mk|ac\.mk|mk|co\.ml|org\.ml|ac\.ml|ml|co\.mm|org\.mm|ac\.mm|mm|co\.mn|org\.mn|ac\.mn|mn|co\.mo|org\.mo|ac\.mo|mo|co\.mp|org\.mp|ac\.mp|mp|co\.mq|org\.mq|ac\.mq|mq|co\.mr|org\.mr|ac\.mr|mr|co\.ms|org\.ms|ac\.ms|ms|co\.mt|org\.mt|ac\.mt|mt|co\.mu|org\.mu|ac\.mu|mu|co\.mv|org\.mv|ac\.mv|mv|co\.mw|org\.mw|ac\.mw|mw|co\.mx|org\.mx|ac\.mx|mx|co\.my|org\.my|ac\.my|my|co\.mz|org\.mz|ac\.mz|mz|co\.na|org\.na|ac\.na|na|co\.nc|org\.nc|ac\.nc|nc|co\.ne|org\.ne|ac\.ne|ne|co\.nf|org\.nf|ac\.nf|nf|co\.ng|org\.ng|ac\.ng|ng|co\.ni|org\.ni|ac\.ni|ni|co\.nl|org\.nl|ac\.nl|nl|co\.no|org\.no|ac\.no|no|co\.np|org\.np|ac\.np|np|co\.nr|org\.nr|ac\.nr|nr|co\.nu|org\.nu|ac\.nu|nu|co\.nz|org\.nz|ac\.nz|nz|co\.om|org\.om|ac\.om|om|co\.pa|org\.pa|ac\.pa|pa|co\.pe|org\.pe|ac\.pe|pe|co\.pf|org\.pf|ac\.pf|pf|co\.pg|org\.pg|ac\.pg|pg|co\.ph|org\.ph|ac\.ph|ph|co\.pk|org\.pk|ac\.pk|pk|co\.pl|org\.pl|ac\.pl|pl|co\.pm|org\.pm|ac\.pm|pm|co\.pn|org\.pn|ac\.pn|pn|co\.pr|org\.pr|ac\.pr|pr|co\.ps|org\.ps|ac\.ps|ps|co\.pt|org\.pt|ac\.pt|pt|co\.pw|org\.pw|ac\.pw|pw|co\.py|org\.py|ac\.py|py|co\.qa|org\.qa|ac\.qa|qa|co\.re|org\.re|ac\.re|re|co\.ro|org\.ro|ac\.ro|ro|co\.rs|org\.rs|ac\.rs|rs|co\.ru|org\.ru|ac\.ru|ru|co\.rw|org\.rw|ac\.rw|rw|co\.sa|org\.sa|ac\.sa|sa|co\.sb|org\.sb|ac\.sb|sb|co\.sc|org\.sc|ac\.sc|sc|co\.sd|org\.sd|ac\.sd|sd|co\.se|org\.se|ac\.se|se|co\.sg|org\.sg|ac\.sg|sg|co\.sh|org\.sh|ac\.sh|sh|co\.si|org\.si|ac\.si|si|co\.sj|org\.sj|ac\.sj|sj|co\.sk|org\.sk|ac\.sk|sk|co\.sl|org\.sl|ac\.sl|sl|co\.sm|org\.sm|ac\.sm|sm|co\.sn|org\.sn|ac\.sn|sn|co\.so|org\.so|ac\.so|so|co\.sr|org\.sr|ac\.sr|sr|co\.ss|org\.ss|ac\.ss|ss|co\.st|org\.st|ac\.st|st|co\.su|org\.su|ac\.su|su|co\.sv|org\.sv|ac\.sv|sv|co\.sx|org\.sx|ac\.sx|sx|co\.sy|org\.sy|ac\.sy|sy|co\.sz|org\.sz|ac\.sz|sz|co\.tc|org\.tc|ac\.tc|tc|co\.td|org\.td|ac\.td|td|co\.tf|org\.tf|ac\.tf|tf|co\.tg|org\.tg|ac\.tg|tg|co\.th|org\.th|ac\.th|th|co\.tj|org\.tj|ac\.tj|tj|co\.tk|org\.tk|ac\.tk|tk|co\.tl|org\.tl|ac\.tl|tl|co\.tm|org\.tm|ac\.tm|tm|co\.tn|org\.tn|ac\.tn|tn|co\.to|org\.to|ac\.to|to|co\.tp|org\.tp|ac\.tp|tp|co\.tr|org\.tr|ac\.tr|tr|co\.tt|org\.tt|ac\.tt|tt|co\.tv|org\.tv|ac\.tv|tv|co\.tw|org\.tw|ac\.tw|tw|co\.tz|org\.tz|ac\.tz|tz|co\.ua|org\.ua|ac\.ua|ua|co\.ug|org\.ug|ac\.ug|ug|co\.uk|org\.uk|ac\.uk|uk|co\.um|org\.um|ac\.um|um|co\.us|org\.us|ac\.us|us|co\.uy|org\.uy|ac\.uy|uy|co\.uz|org\.uz|ac\.uz|uz|co\.va|org\.va|ac\.va|va|co\.vc|org\.vc|ac\.vc|vc|co\.ve|org\.ve|ac\.ve|ve|co\.vg|org\.vg|ac\.vg|vg|co\.vi|org\.vi|ac\.vi|vi|co\.vn|org\.vn|ac\.vn|vn|co\.vu|org\.vu|ac\.vu|vu|co\.wf|org\.wf|ac\.wf|wf|co\.ws|org\.ws|ac\.ws|ws|co\.ye|org\.ye|ac\.ye|ye|co\.yt|org\.yt|ac\.yt|yt|co\.za|org\.za|ac\.za|za|co\.zm|org\.zm|ac\.zm|zm|co\.zw|org\.zw|ac\.zw|zw|co\.ac|org\.ac|ac\.ac|ac|co\.co|org\.co|ac\.co|co)$"
    EXTRACT_TLD_RE = re.compile(pattern)
    return EXTRACT_TLD_RE



# def __rebuild_tld_list__():
#     regex_file = os.path.join(os.path.dirname(__file__), '.tld_regex')
#     try:
#         with codecs.open(regex_file, encoding='utf-8') as f:
#             regex = f.read().strip()
#             EXTRACT_TLD_RE = re.compile(regex)
#             return EXTRACT_TLD_RE
#     except IOError, file_not_found:
#         pass
#
#     page = unicode(urlopen('http://www.iana.org/domains/root/db/').read(), 'utf-8')
#
#     tld_finder = re.compile('<tr class="[^"]*iana-type-(?P<iana_type>\d+).*?<a.*?>\.(?P<tld>\S+?)</a>', re.UNICODE | re.DOTALL)
#     tlds = [(m.group('tld').lower(), m.group('iana_type')) for m in tld_finder.finditer(page)]
#     ccTLDs = [tld for tld, iana_type in tlds if iana_type == "1"]
#     gTLDs = [tld for tld, iana_type in tlds if iana_type != "1"]
#
#     special = ("co", "org", "ac")
#     ccTLDs.sort(key=lambda tld: tld in special)
#     ccTLDs = [
#         '|'.join("%s\.%s" % (s, ccTLD) for s in special) + '|' + ccTLD
#         for ccTLD in ccTLDs
#     ]
#     EXTRACT_TLD_RE_RAW = regex = r"^(?P<registered_domain>.+?)\.(?P<tld>%s)$" % ('|'.join(gTLDs + ccTLDs))
#
#     #print("computed TLD regex: %s", regex)
#
#     try:
#         with codecs.open(regex_file, 'w', 'utf-8') as f:
#             f.write(regex + '\n')
#     except IOError, e:
#         print("unable to save TLD regex file %s: %s", regex_file, e)
#
#     EXTRACT_TLD_RE = re.compile(regex)
#     return EXTRACT_TLD_RE