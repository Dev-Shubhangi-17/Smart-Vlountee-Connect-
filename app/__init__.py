import os
from dotenv import load_dotenv

from flask import Flask
from .config import config_map
from .extensions import db, migrate, jwt, bcrypt, cors, mail

load_dotenv()


def create_app(config_name: str = None) -> Flask:
    """Application factory."""

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, static_folder="static", static_url_path="")

    # Root route to serve static index.html
    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    # Load config
    cfg = config_map.get(config_name, config_map["development"])
    app.config.from_object(cfg)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # CORS — allow frontend origin + localhost dev
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": [app.config["FRONTEND_ORIGIN"], "http://localhost:*", "http://127.0.0.1:*"]}},
        supports_credentials=True,
    )

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.volunteers import volunteers_bp
    from .routes.ngos import ngos_bp
    from .routes.events import events_bp
    from .routes.stats import stats_bp
    from .routes.contact import contact_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(volunteers_bp, url_prefix="/api/volunteers")
    app.register_blueprint(ngos_bp, url_prefix="/api/ngos")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    app.register_blueprint(contact_bp, url_prefix="/api/contact")

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Smart Volunteer Connect API is running!"}

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"error": "Token has expired", "code": "token_expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"error": "Invalid token", "code": "invalid_token"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"error": "Authorization token is missing", "code": "authorization_required"}, 401

    return app
