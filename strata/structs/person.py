from email import utils as __utils__
from strata.utilities.emails import EmailAddress as __EmailAddress__


class Person(object):
    __slots__ = [
        "id",
        "label",
        "email"
    ]

    def __init__(self, *address, **kwd):
        id, label, email = None, None, None


        if len(address) == 2:
            a, b = address[0], address[1]
            if a.find("@") > -1 and a.find(".") > -1:
                a, b = b, a
            email = __EmailAddress__.format(b)
            label = a
        elif len(address) == 1:
            o = __utils__.parseaddr(address[0])
            label, email = o[0], o[1]

        if len(kwd) > 0:
            try:
                id = kwd["id"]
            except KeyError:
                pass

            try:
                if not label:
                    label = kwd["label"]
            except KeyError:
                pass

            try:
                if not email:
                    email = kwd["email"]
            except KeyError:
                pass

        if email is None:
            if label is not None:
                email_address = __EmailAddress__.format(label)
                if email_address is not None:
                    label = None
                    email = email_address.formatted
        self.id = id
        self.label = label
        self.email = email

    def __eq__(self, other):
        if other is None:
            return False

        if self.id is not None:
            if other.id == self.id:
                return True
            return False
        if self.email == other.email:
            return True
        return False

    @property
    def domain(self):
        email = self.email
        if email is None:
            return None

        email = __EmailAddress__.parse(email)
        if email is None:
            return None
        return email.domain

    @property
    def username(self):
        email = self.email
        if email is None:
            return None

        email = __EmailAddress__.parse(email)
        if email is None:
            return None
        return email.username

    @property
    def formatted(self):
        label, email = self.label, self.email
        if not email:
            return label
        if not label:
            return email
        if label and email:
            return __utils__.formataddr((label, email))
        return ""

    @staticmethod
    def parse(address):
        label, username = None, None
        addr = __utils__.parseaddr(address)
        name, email = addr[0], addr[1]
        if email:
            email_address = __EmailAddress__.format(email)
            if email_address is not None:
                username = email_address
            elif len(email) > 0:
                if name is None:
                    name = email
        if name is not None:
            label = name
        return Person(label=label, username=username)

    @staticmethod
    def create(*address, **kwd):
        return Person(*address, **kwd)

    def __repr__(self):
        id = self.id
        name = self.formatted
        if id is not None:
            if name:
                return "%s [#%s]" % (name, str(id))
            return "Person#%s" % str(id)
        if name:
            return name
        return "Person"

    def __str__(self):
        return self.formatted
