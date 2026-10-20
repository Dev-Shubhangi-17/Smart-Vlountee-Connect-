import os
import sys

# Ensure root folder is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()


class VercelPathFixer:
    """WSGI middleware to normalize PATH_INFO and SCRIPT_NAME on Vercel."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        raw_path = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_ORIGINAL_URI")
            or environ.get("REQUEST_URI")
            or environ.get("RAW_URI")
            or environ.get("PATH_INFO", "")
        )

        if raw_path:
            path_only = raw_path.split("?")[0]
            for prefix in ["/api/index.py", "/api/index"]:
                if path_only == prefix:
                    path_only = "/"
                    break
            environ["PATH_INFO"] = path_only if path_only else "/"
            environ["SCRIPT_NAME"] = ""

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathFixer(app.wsgi_app)


# Auto-initialize database tables and demo seed data on serverless startup
with app.app_context():
    try:
        db.create_all()
        from app.models.ngo import NGO
        if NGO.query.count() == 0:
            from seed_db import seed_data
            seed_data()
    except Exception as e:
        app.logger.warning(f"Database auto-init notice: {e}")
