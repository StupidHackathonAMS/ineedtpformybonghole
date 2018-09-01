""" Configuration blueprints for Flask app"""
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
MYSQL_URI = "{driver}://{user}:{password}@{host}:{port}/{db_name}?charset=utf8"


class Config:
    """ Base class for all configs """
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/ineedtp.db'
    PROPAGATE_EXCEPTIONS = True
    MAX_CONTENT_LENGTH = 20000000
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """ Used locally """
    LOG_LEVEL = 'DEBUG'
    TESTING = True
    APP_NAME = os.environ.get('APP_NAME') or '[LOCAL]'


class ProductionConfig(Config):
    """ Put production related config here """
    LOG_LEVEL = 'WARNING'
    APP_NAME = os.environ.get('APP_NAME') or 'ineedtpformybonghole'


config = {'development': DevelopmentConfig,
          'production': ProductionConfig,
          'default': DevelopmentConfig}
