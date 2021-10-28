from flask import Flask
import pytest


def create_app():
    app = Flask(__name__)

    @app.cli.command()
    def test():
        pytest.main(['-s', '--rootdir', '.'])

    with app.app_context():
        from app.modules import redis as app_redis
        app_redis.init_redis()

    """
    Import blueprints
    """

    from app.modules.elevator import bp as elevator
    app.register_blueprint(elevator)

    from app.modules.tbike import bp as tbike
    app.register_blueprint(tbike)

    return app
