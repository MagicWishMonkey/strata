from .. import toolkit
from ..errors import *
from ..context import Extension
from .who_api import who_api_call


class Who(Extension):
    __settings__ = None

    def __init__(self, *ctx):
        Extension.__init__(self, *ctx)

    @property
    def settings(self):
        settings = Who.__settings__
        if settings is not None:
            return settings
        cfg = self.config
        who_cfg = cfg.who
        settings = {
            "client_id": who_cfg.client_id,
            "client_secret": who_cfg.client_secret,
            "scope": who_cfg.scope,
            "response_type": who_cfg.response_type,
            "gateway_uri": who_cfg.gateway_uri,
            "gateway_api_uri": who_cfg.gateway_api_uri,
            "redirect_uri": who_cfg.redirect_uri,
            "authorization_uri": who_cfg.authorization_uri,
            "fetch_token_uri": who_cfg.fetch_token_uri
        }
        Who.__settings__ = settings
        return settings

    @property
    def who_api_uri(self):
        return self.settings["gateway_api_uri"]

    def create_connect_request(self, **state):
        settings = self.settings
        uri = settings["gateway_uri"]
        client_id = settings["client_id"]
        client_secret = settings["client_secret"]
        redirect_uri = settings["redirect_uri"]
        response_type = settings["response_type"]
        uri = "%s?response_type=%s&redirect_url=%s&client_id=%s&client_secret=%s" % (
            uri, response_type, redirect_uri, client_id, client_secret
        )
        if state:
            state = toolkit.json(state)
            uri = "%s&state=%s" % (uri, state)
        return uri

# @Who.plugin
# def save_access_code(self, code, token=None):
#     member_id = self.member_id
#     if member_id is None:
#         raise AccessDeniedError("You are not logged in.")
#
#     if token is None:
#         token = self.fetch_token(code)
#     self.query(
#         "UPDATE members SET access_code=@code, access_token=@token, access_code_created=CURRENT_TIMESTAMP , access_token_created=CURRENT_TIMESTAMP WHERE id=@id;",
#         code=code,
#         token=token,
#         id=member_id
#     ).update()
#     self.member.access_token = token


# @Who.plugin
# def refresh_token(self, *member):
#     member = self.member if len(member) == 0 else member[0]
#     if member is None:
#         raise AccessDeniedError("You are not logged in.")
#
#
#     member_id = member.id
#     code = self.query("SELECT access_code FROM members WHERE id=@id;", id=member_id).scalar()
#     if code is None:
#         return
#
#     token = self.fetch_token(code)
#     self.query(
#         "UPDATE members SET access_code=@code, access_token=@token, access_code_created=CURRENT_TIMESTAMP , access_token_created=CURRENT_TIMESTAMP WHERE id=@id;",
#         code=code,
#         token=token,
#         id=member_id
#     ).update()
#     member.access_token = token


@Who.plugin
def activate(self, code):
    token = self.api_call("fetch_token", code)
    session = self.api_call("fetch_session", token)

    member_object = session["member"]
    id = member_object["id"]
    username = member_object["username"]
    label = member_object["label"]
    member = self.members.get(id)
    if member is None:
        member = self.members.get(username)
        if member is None:
            self.members.register(id=id, label=label, username=username)


    self.impersonate(member)
    self.members.update_member_token(token=token, code=code)


    # token = self.who.fetch_token(code)
    # session = self.who.fetch_api_session(token)
    #
    # member_object = session["member"]
    # id = member_object["id"]
    # username = member_object["username"]
    # label = member_object["label"]
    # member = self.members.get(id)
    # if member is None:
    #     member = self.members.get(username)
    #     if member is None:
    #         self.members.register(id=id, label=label, username=username)
    #
    # self.impersonate(member)
    # self.members.update_member_token(token=token, code=code)

@Who.plugin
def new_api_call(self, uri):
    fn = who_api_call(self)
    fn = toolkit.curry(fn, uri)
    return fn


@Who.plugin
def api_call(self, uri, *args, **kwd):
    fn = who_api_call(self)
    return fn(uri, *args, **kwd)


@Who.plugin
def contacts(self):
    return self.api_call("member/contacts")


# @Who.plugin
# def create_api_scope(self, label):
#     return self.api_call("partners/create_scope/%s" % label)



# @Who.plugin
# def fetch_token(self, code):
#     settings = self.settings
#     client_id = settings["client_id"]
#     client_secret = settings["client_secret"]
#     uri = settings["fetch_token_uri"]
#
#     params = toolkit.encode_url_params(
#         client_id=client_id,
#         client_secret=client_secret,
#         code=code
#     )
#     object = None
#     try:
#         response = toolkit.web_post(uri, params)
#         object = toolkit.unjson(response)
#     except Exception, ex:
#         message = "Error fetching token: %s" % ex.message
#         raise RepositoryError(message, inner=ex)
#
#     try:
#         token = object["access_token"]
#         return token
#     except Exception, ex:
#         message = "Error extracting token from response: %s" % ex.message
#         raise RepositoryError(message)
#
#
# @Who.plugin
# def fetch_api_session(self, token):
#     uri = self.who_api_uri
#     uri = "%s/session?token=%s" % (uri, token)
#     session = toolkit.unjson(toolkit.web_get(uri))
#     return session








