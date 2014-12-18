from .sequences import *
from .who import Who
from .members import Members
from .sessions import Sessions
from .scopes import Scopes

class Context:

    def sequence(self, *count):
        return SequenceGenerator().generate(*count)

    def impersonate(self, member):
        if isinstance(member, (int, basestring)) is True:
            member = self.members.get(member)
            if member is None:
                return self.clear()

        if toolkit.is_model(member) is False:
            return self.clear()
        self.sessions.create(member)
        return self

    @property
    def who(self):
        return Who(self)

    @property
    def members(self):
        return Members(self)

    @property
    def sessions(self):
        return Sessions(self)

    @property
    def scopes(self):
        return Scopes(self)