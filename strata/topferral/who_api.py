from .. import toolkit
from ..errors import *




def who_api_call(self):
    settings = self.settings

    def call(uri, *args, **kwd):
        def parse(response):
            object = None
            try:
                object = toolkit.unjson(response)
            except Exception, ex:
                message = "Who@ Endpoint Error - %s" % ex.message
                raise APIError(message, inner=ex)

            return object


        def fetch_token(*code):
            client_id = settings["client_id"]
            client_secret = settings["client_secret"]
            uri = settings["fetch_token_uri"]
            code = code[0] if code else self.member.access_code
            params = toolkit.encode_url_params(
                client_id=client_id,
                client_secret=client_secret,
                code=code
            )

            response = None
            try:
                response = toolkit.web_post(uri, params)
            except Exception, ex:
                message = "Error making request - %s" % ex.message
                raise APIError(message, inner=ex)

            object = parse(response)
            token = None
            try:
                token = object["access_token"]
            except Exception, ex:
                message = "Error extracting token from response - %s" % ex.message
                raise APIError(message)

            if self.member is None:
                return token

            queries = self.query_buffer()
            queries.append(
                "UPDATE members SET access_code=@code, access_token=@token, access_code_created=CURRENT_TIMESTAMP , access_token_created=CURRENT_TIMESTAMP WHERE id=@id;",
                code=code,
                token=token,
                id=self.member.id
            )

            queries.append(
                "UPDATE sessions SET token=@token, accessed=CURRENT_TIMESTAMP WHERE id=@id;",
                token=token,
                id=self.session.id
            )
            queries.execute()

            self.member.access_code = code
            self.member.access_token = token
            self.session.token = token
            return token

        def fetch_session(*token):
            token = token[0] if token else self.member.access_token
            endpoint = "%s/session?token=%s" % (settings["gateway_api_uri"], token)

            response = toolkit.web_get(endpoint)
            object = parse(response)
            return object

        if uri.startswith("fetch_"):
            if uri == "fetch_token":
                return fetch_token(*args)
            elif uri == "fetch_session":
                return fetch_session(*args)

        if uri[0] == "/":
            uri = uri[1:]

        params = None if not kwd else toolkit.encode_url_params(**kwd)
        token = self.member.access_token
        endpoint = "%s/%s?token=%s" % (settings["gateway_api_uri"], uri, token)
        if params:
            endpoint = "%s&%s" % (endpoint, params)


        print endpoint
        response = toolkit.web_get(endpoint)
        try:
            object = parse(response)
            return object
        except:
            token = fetch_token()
            endpoint = "%s/%s?token=%s" % (settings["gateway_api_uri"], uri, token)
            if params:
                endpoint = "%s&%s" % (endpoint, params)

            response = toolkit.web_get(endpoint)
            object = parse(response)
            return object


    return call

