# from fuze.utilities import chars as __chars__
# from fuze.structs.buffers import RollingCache as __RollingCache__
# from fuze.utilities import tlds as __tldlib__
#
#
# class __domain_util__:
#     __webmails__ = {}
#     __punctuation__ = "".join([c for c in __chars__.PUNCTUATION if c != "."])
#     __cache__ = __RollingCache__(1000)
#     __tlds__ = set(["com", "net", "org"])
#
#
#     @staticmethod
#     def register_webmails(*domains):
#         tbl = __domain_util__.__webmails__
#         for domain in domains:
#             val = domain.strip().lower()
#             if val:
#                 tbl[val] = val
#
#     @staticmethod
#     def is_webmail(domain):
#         tbl = __domain_util__.__webmails__
#         try:
#             return True if tbl[domain.strip().lower()] is not None else False
#         except:
#             return False
#
#     @staticmethod
#     def format(txt):
#         def filter(txt):
#             table = __chars__.trans_table()
#             return txt.translate(table, __domain_util__.__punctuation__)
#
#         txt = txt.strip()
#         if len(txt) > 255:
#             if txt.find("@") > -1:
#                 txt = txt.split("@")[1]
#         txt = filter(txt)
#         cnt = len(txt)
#         if cnt == 0 or cnt > 275 or txt.find(".") == -1:
#             return None
#         return txt.lower()
#
#     @staticmethod
#     def cache(key, *val):
#         if len(val) == 0:
#             d = __domain_util__.__cache__.get(key)
#             return d.clone() if d is not None else d
#
#         val = val[0]
#         __domain_util__.__cache__.set(key, val.clone())
#         return val
#
#
#     @staticmethod
#     def parse(txt):
#         txt = txt.strip()
#         if len(txt) == 0:
#             return None
#         domain = DomainName(txt)
#         val = __domain_util__.format(txt)
#         if val is None:
#             return domain
#
#         key = val
#         cached = __domain_util__.cache(key)
#         if cached:
#             return cached
#
#         parts = val.split(".")
#         tld = parts[len(parts) - 1]
#         if len(parts[0]) == 0:
#             return domain
#
#         tlds = __domain_util__.__tlds__
#         if len(parts) == 2:
#             if tld in tlds:
#                 domain_name = parts[0]
#                 domain_name = "%s.%s" % (domain_name, tld)
#                 domain.domain = domain_name
#                 domain.formatted = val
#                 domain.tld = tld
#                 domain.invalid = False
#                 __domain_util__.cache(key, domain)
#                 return domain
#
#
#         tdx = __tldlib__.extract(val)
#         tld = tdx.tld
#         domain_name = tdx.domain
#         if tld == "" or domain_name == "":
#             __domain_util__.cache(key, domain)
#             return domain
#
#         domain_name = "%s.%s" % (domain_name, tld)
#         root = None
#         if tdx.subdomain != "":
#             root = domain_name
#             domain_name = "%s.%s" % (tdx.subdomain, domain_name)
#
#         if root is not None:
#             root = DomainName(
#                 root,
#                 formatted=root,
#                 domain=root,
#                 invalid=False,
#                 tld=tld
#             )
#
#             domain.root = root
#
#         domain.formatted = val
#         domain.domain = domain_name
#         domain.invalid = False
#         domain.tld = tld
#
#
#         if tld not in tlds:
#             tlds = list(tlds)
#             tlds.append(tld)
#             __domain_util__.__tlds__ = set(tlds)
#
#         __domain_util__.cache(key, domain)
#         return domain
#
#
#         # tdx = tldlib.extract(val)
#         # tld = tdx.tld
#         # domain = tdx.domain
#         # if tld == "" or domain == "":
#         #     o.valid = False
#         #     return helper.set_cached(val, o)
#         #
#         # o.tld = tld
#         # o.root = "%s.%s" % (domain, tld)
#         # if Webmails.is_webmail(o.root) is True:
#         #     o.webmail = True
#         #
#         # if tdx.subdomain != "":
#         #     o.domain = "%s.%s" % (tdx.subdomain, o.root)
#         #     o.is_sub_domain = True
#         # else:
#         #     o.domain = o.root
#         #
#         # o.formatted = o.domain
#         #
#         #
#         # if chars.find(tld[len(tld)-1]) == -1 or chars.find(tld[0]) == -1:
#         #     o.valid = False
#         # else:
#         #     o.valid = True
#
#
#
#
# class DomainName(object):
#     __slots__ = [
#         "value",
#         "formatted",
#         "domain",
#         "root",
#         "tld",
#         "invalid"
#     ]
#
#
#     def __init__(self, value, **kwd):
#         self.value = value
#         self.formatted = None
#         self.domain = None
#         self.root = None
#         self.tld = None
#         self.invalid = True
#         if len(kwd) > 0:
#             try:
#                 self.formatted = kwd["formatted"]
#             except KeyError:
#                 pass
#
#             try:
#                 self.domain = kwd["domain"]
#             except KeyError:
#                 pass
#
#             try:
#                 self.root = kwd["root"]
#             except KeyError:
#                 pass
#
#             try:
#                 self.tld = kwd["tld"]
#             except KeyError:
#                 pass
#
#             try:
#                 self.invalid = kwd["invalid"]
#             except KeyError:
#                 pass
#
#     @property
#     def is_sub_domain(self):
#         if self.root is None:
#             return False
#         return True
#
#     @property
#     def valid(self):
#         if self.invalid is False:
#             return True
#         return False
#
#     @property
#     def is_webmail(self):
#         if self.invalid is True:
#             return False
#         return __domain_util__.is_webmail(self.domain)
#
#     def clone(self):
#         root = self.root
#         if root is not None:
#             root = root.clone()
#         return DomainName(
#             self.value,
#             formatted=self.formatted,
#             domain=self.domain,
#             root=root,
#             tld=self.tld,
#             invalid=self.invalid
#         )
#
#     @staticmethod
#     def parse(txt):
#         return __domain_util__.parse(txt)
#
#     @staticmethod
#     def is_valid(txt):
#         o = __domain_util__.parse(txt)
#         if o:
#             if o.invalid is False:
#                 return True
#         return False
#
#     @staticmethod
#     def format(txt):
#         o = __domain_util__.parse(txt)
#         if o:
#             if o.invalid is False:
#                 return o.formatted
#         return None
#
#     def __repr__(self):
#         if self.formatted:
#             return self.formatted
#         if self.value:
#             return self.value
#         return "DomainName"
#
#     def __str__(self):
#         if self.formatted:
#             return self.formatted
#         return self.value
#
#
# def register_webmails(*domains):
#     __domain_util__.register_webmails(*domains)