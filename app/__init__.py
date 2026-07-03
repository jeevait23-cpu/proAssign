def create_app(test_config=None, user_repo=None, project_repo=None):
    from flask import Flask

    from .config import Config
    from .db import create_project_repository, create_user_repository
    from .routes import auth_bp, dashboard_bp

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.user_repo = user_repo or create_user_repository(app.config)
    app.project_repo = project_repo or create_project_repository(app.config)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app
