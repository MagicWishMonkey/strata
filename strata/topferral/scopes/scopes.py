from ... import toolkit
from ...errors import *
from .. import Repository


class Scopes(Repository):
    def lookup(self, *labels):
        single = False
        if len(labels) == 1:
            if isinstance(labels[0], list) is False:
                single = True

        member_id = self.member_id
        if member_id is None:
            return None if single is True else []

        labels = toolkit.unroll(labels)
        keys = []
        for label in labels:
            scope_id = self.query("SELECT id FROM scopes WHERE member_id=@member_id AND label=@label;", member_id=member_id, label=label).scalar()
            if scope_id is not None:
                keys.append(scope_id)
        if single is True:
            return keys[0] if len(keys) > 0 else None
        return keys


    def extend(self, scopes):
        for scope in scopes:
            scope_id = scope.id
            # scope_object = self.who.api_call("partners/scope/%s" % str(scope_id))
            # scope.ratings = scope_object["ratings"]

            ratings = self.who.api_call("/partner/ratings/%s" % str(scope_id))
            scope.ratings = ratings

        return scopes


@Scopes.plugin
def create(self, label, description=None, website=None):
    member = self.member
    if member is None:
        raise AccessDeniedError("You are not logged in!")

    member_id = member.id
    scope = self.who.api_call("partners/create_scope/%s" % label)
    #scope = self.who.create_api_scope(label)
    scope_id = scope["id"]
    model = self.get(scope_id)
    if model is not None:
        self.query(
            "UPDATE scopes SET label=@label, description=@description, website=@website WHERE id=@id;",
            label=label,
            description=description,
            website=website,
            id=scope_id
        ).update()
        return model

    self.query(
        "INSERT INTO scopes (id, label, member_id, description, website) VALUES (@id, @label, @member_id, @description, @website);",
        id=scope_id,
        label=label,
        member_id=member_id,
        description=description,
        website=website
    ).insert()

    scope = self.get(scope_id)
    return scope


@Scopes.plugin
def upvote(self, scope, comment):
    member = self.member
    if member is None:
        raise AccessDeniedError("You are not logged in!")

    scope_id = scope if isinstance(scope, int) is True else None
    if scope_id is None:
        scope_id = scope.id

    self.who.api_call("/partner/upvote/%s" % str(scope_id), comment=comment)


@Scopes.plugin
def downvote(self, scope, comment):
    member = self.member
    if member is None:
        raise AccessDeniedError("You are not logged in!")

    scope_id = scope if isinstance(scope, int) is True else None
    if scope_id is None:
        scope_id = scope.id

    self.who.api_call("/partner/downvote/%s" % str(scope_id), comment=comment)


@Scopes.plugin
def ratings(self, scope):
    member = self.member
    if member is None:
        raise AccessDeniedError("You are not logged in!")

    scope_id = scope if isinstance(scope, int) is True else None
    if scope_id is None:
        scope_id = scope.id

    ratings = self.who.api_call("/partner/ratings/%s" % str(scope_id))
    return ratings
