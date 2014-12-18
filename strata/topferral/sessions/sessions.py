from ... import toolkit
from ...errors import *
from .. import Repository


class Sessions(Repository):
    def lookup(self, *tokens):
        single = False
        if len(tokens) == 1:
            if isinstance(tokens[0], list) is False:
                single = True

        tokens = toolkit.unroll(tokens)
        keys = []
        for token in tokens:
            session_id = self.query("SELECT id FROM sessions WHERE token=@token;", token=token).scalar()
            if session_id is not None:
                keys.append(session_id)
        if single is True:
            return keys[0] if len(keys) > 0 else None
        return keys


@Sessions.plugin
def restore(self, token):
    id = None if isinstance(token, int) is False else token
    if id is None:
        id = self.lookup(token)
    if id is None:
        return self.create()

    session = self.get(id)
    self.query("UPDATE sessions SET accessed=CURRENT_TIMESTAMP WHERE id={id};".format(id=id)).update()
    member_id = session.member_id
    if member_id is not None:
        self.query("UPDATE members SET accessed=CURRENT_TIMESTAMP WHERE id={id};".format(id=member_id)).update()
    self.attach(session)
    return session


@Sessions.plugin
def create(self, *member):
    member = None if len(member) == 0 else member[0]
    member_id = None if member is None else member.id
    if member_id is not None:
        session = self.session
        if session is not None:
            if session.member_id is None or session.member_id == member_id:
                session_id = session.id
                self.query(
                    "UPDATE sessions SET member_id=@member_id, accessed=CURRENT_TIMESTAMP WHERE id=@id;",
                    id=session_id,
                    member_id=member_id
                ).update()
                return self.restore(session_id)

    ip_address = self.ip_address
    user_agent_string = self.user_agent_string
    token = toolkit.guid(32)
    id = self.query(
        "INSERT INTO sessions (token, member_id, ip_address, user_agent_string, created, accessed) VALUES (@token, @member_id, @ip_address, @user_agent_string, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);",
        token=token,
        member_id=member_id,
        ip_address=ip_address,
        user_agent_string=user_agent_string
    ).insert()

    session = self.get(id)
    self.attach(session)
    return session



@Sessions.plugin
def destroy(self, *session):
    session = session[0] if len(session) > 0 else self.session
    if not session:
        return

    if toolkit.is_model(session) is False:
        session = self.get(session)
        if not session:
            return

    session_id = session.id
    self.query("DELETE FROM sessions WHERE id=@id;", id=session_id).update()
    if self.session is not None and self.session.id == session_id:
        self.clear()

