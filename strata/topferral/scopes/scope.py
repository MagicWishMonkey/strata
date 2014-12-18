from ... import system
from .. import Model


class Scope(Model):
    __slots__ = [
        "id",
        "label",
        "member_id",
        "description",
        "website",
        "ratings",
        "created"
    ]
    __defaults__ = {
        "ratings": 0
    }

    @property
    def owner(self):
        return self.ctx.members.get(self.member_id)

    # @property
    # def ratings(self):
    #     return self.ctx.scopes.ratings(self)

    def upvote(self, comment):
        return self.ctx.scopes.upvote(self, comment)

    def downvote(self, comment):
        return self.ctx.scopes.downvote(self, comment)