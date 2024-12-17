# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Corrected login view to use the blueprint prefix
    login.login_view = 'routes.login'  # Use 'routes.login' because the 'login' route is in the 'routes' blueprint

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app


@login.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
