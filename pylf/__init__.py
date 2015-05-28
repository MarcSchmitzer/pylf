"""Main module of the application."""

from pyramid.config import Configurator
from pyramid.i18n import default_locale_negotiator
from webob.acceptparse import Accept

def main(global_config, **settings):  # pylint: disable=unused-argument
    """Main function of the application."""
    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', 'pylf')

    config = Configurator(
        locale_negotiator=LocaleNegotiator.from_settings(settings),
        settings=settings,
    )
    config.add_translation_dirs('pylf:locale/')

    config.add_request_method(
        lambda request: request.registry.settings,
        "settings",
        property=True,
        reify=True,
    )

    config.add_static_view('static', 'static')
    config.commit()

    config.include(".root")
    config.include(".mounts")
    config.include(".directory")
    config.include(".file")
    config.include(".util")
    config.include(".icons")

    return config.make_wsgi_app()


class LocaleNegotiator:
    """Locale negotiator that supports the "Accept-Language" HTTP
    header.
    """
    @classmethod
    def from_settings(cls, settings):
        """Create a new instance based on the `settings` dict.

        The locales supported by the application are read from the
        "locales" key. The format of the value is the same as that of
        the Accept-Language header, i.e.:

          <locale1>;q=<q1>,<locale2>;q=<q2>,...

        The q-values indicate the quality of the locale, but are
        optional.
        """
        locales = list(Accept.parse(settings.get("locales", "")))
        return cls(locales)

    def __init__(self, locales):
        """Constructor.

        Args:
          locales (sequence): Locale names or pairs of locale, quality
            values.
        """
        self.locales = locales

    def __call__(self, request):
        """Negotiate the request locale.

        Uses the pyramid default negotiator the pick up the locale
        from the request parameters or the session. Then falls back to
        the Accept-Language header.
        """
        loc = default_locale_negotiator(request)
        if not loc:
            loc = request.accept_language.best_match(self.locales)
        return loc
