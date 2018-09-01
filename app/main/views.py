import os
import time
import random

from . import main_blueprint
from flask import request, jsonify, send_file
from app import db
from sqlalchemy import desc, asc
from app.models import TPRequest
from app.auth import requires_auth
from werkzeug.utils import secure_filename
from geolite2 import geolite2

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@main_blueprint.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Request-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONSk')
    return response


@main_blueprint.route('/getTPRequests', methods=['GET'])
def get_requests():
    fulfilled = bool(request.args.get('fulfilled', ''))
    filter_fulfiller = TPRequest.fulfilledAt != None if fulfilled else TPRequest.fulfilledAt == None
    reqs = [i.json for i in TPRequest
            .query
            .filter(filter_fulfiller)
            .order_by(asc(TPRequest.createdAt))
            .all()]
    return jsonify({'response': reqs})


@main_blueprint.route('/createTPRequest', methods=['POST'])
def create_request():
    request_json = request.get_json()
    req = TPRequest(name=request_json['name'],
                    message=request_json['message'],
                    location=extract_location(request))
    db.session.add(req)
    db.session.commit()
    return jsonify({'response': req.json})


@main_blueprint.route('/getDetail', methods=['GET'])
def get_request():
    request_id = request.args.get('id')
    req = TPRequest.query.filter(TPRequest.id == request_id).one_or_none()
    return jsonify({'response': req.json if req else None})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_location(request):
    reader = geolite2.reader()
    user_ip = request.remote_addr
    if user_ip == '127.0.0.1':
        user_ip = '62.163.105.195'

    ip_info = reader.get(user_ip)
    location = '{} {}'.format(ip_info['country']['names']['en'], ip_info['city']['names']['en'])
    return location


@main_blueprint.route('/upload', methods=['POST'])
def upload_responce():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'message': 'no file found'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'no file found'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.abspath(os.path.join('app/static/img', filename))
            file.save(save_path)

            request_id = request.form['id']
            req = TPRequest.query.filter(TPRequest.id == request_id).one_or_none()
            if req:
                req.message = request.form['message']
                req.img_url = '{}/app/static/img/{}'.format(request.host, filename)
                req.fulfilledAt = int(time.time())
                db.session.add(req)
                db.session.commit()
            return jsonify({'response': req.json if req else None})


@main_blueprint.route('/install')
@requires_auth
def install():
    db.create_all()
    return 'ok'


@main_blueprint.route('/getRandom')
def get_random():
    path_to_images = os.path.abspath('app/static/img')
    filename = random.choice(os.listdir(path_to_images))
    return send_file(os.path.join(path_to_images, filename))