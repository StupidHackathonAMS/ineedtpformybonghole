""" Custom error pages """
from flask import render_template
from . import main_blueprint


@main_blueprint.app_errorhandler(403)
def page_forbidden(exc):
    """ Forbidden handler """
    return render_template('error.html', exc=exc), 403


@main_blueprint.app_errorhandler(404)
def page_not_found(exc):
    """ Not found handler """
    return render_template('error.html', exc=exc), 404


@main_blueprint.app_errorhandler(500)
def internal_server_error(exc):
    """ Internal error handler """
    return render_template('error.html', exc=exc), 500
