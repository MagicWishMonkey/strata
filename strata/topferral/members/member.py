from ... import system
from .. import Model


class Member(Model):
    __slots__ = [
        "id",
        "label",
        "username",
        "avatar",
        "access_code",
        "access_token",
        "registered"
    ]

    def bind(self, **kwd):
        if kwd["avatar"] is None:
            kwd["avatar"] = system.default_member_avatar
        return Model.bind(self, **kwd)

    def deflate(self):
        return {
            "id": self.id,
            "label": self.label,
            "username": self.username,
            "avatar": self.avatar,
            "registered": self.registered
        }

    @property
    def scopes(self):
        return self.ctx.members.get_member_scopes(self)

    def __str__(self):
        if self.username is not None:
            return "%s %s" % (Model.__str__(self), self.username)
        return Model.__str__(self)