
from pyramid.i18n import default_locale_negotiator
from webob.acceptparse import Accept


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


def includeme(config):
    negotiator = LocaleNegotiator.from_settings(config.get_settings())
    config.set_locale_negotiator(negotiator)
