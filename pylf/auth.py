
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.security import forget


def check_auth(username, password, request):
    userdb = request.context.mount.userdb
    if userdb.authenticate(username, password):
        return ()
    return None


class AuthzPolicy:
    def permits(self, context, principals, permission):
        return True  # FIXME


def forbidden_view(request):
    response = HTTPUnauthorized()
    response.headers.update(forget(request))
    return response


def includeme(config):
    config.add_view(
        forbidden_view,
        context=HTTPForbidden,
    )
    authn_policy = BasicAuthAuthenticationPolicy(
        check=check_auth,
        realm="PYLF",
    )
    config.set_authorization_policy(AuthzPolicy())
    config.set_authentication_policy(authn_policy)
