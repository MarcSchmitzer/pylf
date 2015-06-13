
from pyramid.authentication import BasicAuthAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from pyramid.security import forget


class AuthnPolicy(BasicAuthAuthenticationPolicy):
    def __init__(self):
        BasicAuthAuthenticationPolicy.__init__(
            self,
            check=check_auth,
        )

    def forget(self, request):
        realm = request.context.mount.auth_realm
        return [('WWW-Authenticate', 'Basic realm="%s"' % realm)]


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
    config.set_authorization_policy(AuthzPolicy())
    config.set_authentication_policy(AuthnPolicy())
