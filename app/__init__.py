
from flask import Flask, render_template, request


from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config.config import Config


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)


def create_app():
    

    app = Flask(__name__)
    


    # Load configuration
    app.config.from_object(Config)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------
    # Security: Session Cookies
    # --------------------------------------------------

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Secure cookies only in production
    if app.config.get("FLASK_ENV") == "production":
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["WTF_CSRF_SSL_STRICT"] = True
    else:
        app.config["SESSION_COOKIE_SECURE"] = False
        app.config["WTF_CSRF_SSL_STRICT"] = False

    # --------------------------------------------------
    # Initialize extensions
    # --------------------------------------------------

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"

    # --------------------------------------------------
    # Flask-Login user loader
    # --------------------------------------------------

    @login_manager.user_loader
    def load_user(user_id):

        
        from app.models.user import User

        user = db.session.get(
            User,
            int(user_id)
        )
        
        

        return user

    # --------------------------------------------------
    # Create database tables
    # --------------------------------------------------

    with app.app_context():

        from app.models.user import User
        from app.models.document import Document
        from app.models.document_record import DocumentRecord
        from app.models.match_result import MatchResult

        db.create_all()

    # --------------------------------------------------
    # Register routes
    # --------------------------------------------------

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.document import document
    app.register_blueprint(document)

    # --------------------------------------------------
    # Security Response Headers
    # --------------------------------------------------

    @app.after_request
    def add_security_headers(response):

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )

        response.headers["Permissions-Policy"] = (
            "camera=(), "
            "microphone=(), "
            "geolocation=()"
        )

        return response

    # --------------------------------------------------
    # Home page
    # --------------------------------------------------

    @app.route("/")
    def home():
        return render_template("home.html")

    # --------------------------------------------------
    # Temporary 500 error logger
    # --------------------------------------------------

    

    return app

        