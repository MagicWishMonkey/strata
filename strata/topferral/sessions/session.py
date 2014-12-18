from ... import system
from .. import Model


class Session(Model):
    __slots__ = [
        "id",
        "token",
        "member_id",
        "created",
        "accessed"
    ]

    @property
    def guest(self):
        return True if self.member_id is None else False

    # def deflate(self):
    #     return {
    #         "id": self.id,
    #         "label": self.label,
    #         "username": self.username,
    #         "avatar": self.avatar,
    #         "registered": self.registered
    #     }

    #
    # @property
    # def networks(self):
    #     ctx = self.ctx
    #     networks = ctx.query(
    #         "SELECT NetworkID FROM network_member WHERE MemberID=%s;" % str(self.id)
    #     ).scalars()
    #     networks.append(self.network_id)
    #     networks = list(set(networks))
    #     networks = ctx.networks.get(networks)
    #     return networks

    @property
    def member(self):
        member_id = self.member_id
        if member_id is None:
            return None

        ctx = self.ctx
        member = ctx.members.get(member_id)
        return member

    def destroy(self):
        ctx = self.ctx
        ctx.sessions.destroy(self)


    def __str__(self):
        if self.username is not None:
            return "%s %s" % (Model.__str__(self), self.username)
        return Model.__str__(self)