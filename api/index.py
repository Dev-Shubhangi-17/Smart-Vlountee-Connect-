import os
import sys
from urllib.parse import parse_qs, urlencode

# Ensure root folder is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()


class VercelRouteFixer:
    """WSGI middleware to extract the captured route parameter from Vercel rewrites."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get("QUERY_STRING", "")
        if "__route__=" in query_string:
            params = parse_qs(query_string, keep_blank_values=True)
            routes = params.pop("__route__", None)
            if routes and routes[0]:
                route = routes[0].strip()
                if not route.startswith("/"):
                    route = "/" + route
                environ["PATH_INFO"] = f"/api{route}"
                environ["QUERY_STRING"] = urlencode(params, doseq=True)

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelRouteFixer(app.wsgi_app)


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
