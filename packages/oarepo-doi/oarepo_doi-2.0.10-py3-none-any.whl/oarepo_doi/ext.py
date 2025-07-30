from .config import NOTIFICATIONS_BUILDERS
from deepmerge import conservative_merger

class OARepoDOI(object):
    """OARepo DOI extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["oarepo-doi"] = self

    def init_config(self, app):
        """Initialize configuration."""
        if "DATACITE_URL" not in app.config:
            app.config["DATACITE_URL"] = "https://api.datacite.org/dois"
        if "DATACITE_MODE" not in app.config:
            app.config["DATACITE_MODE"] = "ON_EVENT"
        if "DATACITE_SPECIFIED_ID" not in app.config:
            app.config["DATACITE_SPECIFIED_ID"] = False

        app_notification_builders = app.config.setdefault(
            "NOTIFICATIONS_BUILDERS", {}
        )
        app.config["NOTIFICATIONS_BUILDERS"] = conservative_merger.merge(
            app_notification_builders, NOTIFICATIONS_BUILDERS
        )