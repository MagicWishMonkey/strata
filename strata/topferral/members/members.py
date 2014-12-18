from ... import toolkit
from ...errors import *
from .. import Repository


class Members(Repository):
    def lookup(self, *keys):
        emails = toolkit.unroll(keys)
        emails = [toolkit.format_email(email) for email in emails]
        emails = [e for e in emails if e is not None]
        if len(emails) == 0:
            return []
        keys = []
        for email in emails:
            member_id = self.query("SELECT id FROM members WHERE username=@email;", email=email).scalar()
            if member_id is not None:
                keys.append(member_id)
        return keys


@Members.plugin
def get_member_scopes(self, *member):
    member = None if len(member) == 0 else member[0]
    member_id = None if member is None else member.id
    if member_id is None:
        raise AccessDeniedError("You are not logged in.")
    keys = self.query("SELECT id FROM scopes WHERE member_id=@id;", id=member_id).scalars()
    return [] if len(keys) == 0 else self.scopes.get(keys)


@Members.plugin
def register(self, id=None, label=None, username=None, token=None, code=None):
    assert username is not None, "The username parameter is missing."
    assert label is not None, "The label parameter is missing."
    if toolkit.is_email(username) is False:
        raise InvalidEmailError("The username is not a valid email address: %s" % username)

    email = toolkit.format_email(username)
    if self.get(email) is not None:
        raise RepositoryError("A member with that username has already registered: %s" % username)

    if id is None:
        id = self.sequence()
    try:
        self.query(
            "INSERT INTO members (id, label, username, registered, accessed) VALUES (@id, @label, @username, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);",
            id=id,
            username=email,
            label=label
        ).insert()
    except Exception, ex:
        raise RepositoryError("Error while creating member record: %s" % ex.message, inner=ex)

    member = self.get(id)
    self.sessions.create(member)
    return member



@Members.plugin
def update_member_token(self, token=None, code=None):
    member = self.member
    if member is None:
        raise AccessDeniedError("You are not logged in.")

    member_id = member.id
    if token is not None and code is not None:
        self.query(
            "UPDATE members SET access_token=@token, access_code=@code, access_token_created=CURRENT_TIMESTAMP, access_code_created=CURRENT_TIMESTAMP WHERE id=@id;",
            token=token,
            code=code,
            id=member_id
        ).update()
    elif token is not None:
        self.query(
            "UPDATE members SET access_token=@token, access_token_created=CURRENT_TIMESTAMP WHERE id=@id;",
            token=token,
            id=member_id
        ).update()
    elif code is not None:
        self.query(
            "UPDATE members SET access_token=null, access_code=@code, access_code_created=CURRENT_TIMESTAMP WHERE id=@id;",
            code=code,
            id=member_id
        ).update()
