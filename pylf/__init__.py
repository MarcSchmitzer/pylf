"""Main module of the application."""

from pyramid.config import Configurator


def main(global_config, **settings):  # pylint: disable=unused-argument
    """Main function of the application."""
    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', 'pylf')

    config = Configurator(
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

    config.include(".auth")
    config.include(".i18n")
    config.include(".root")
    config.include(".mounts")
    config.include(".directory")
    config.include(".file")
    config.include(".util")
    config.include(".icons")

    return config.make_wsgi_app()
