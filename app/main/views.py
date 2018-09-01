import os
import time
from . import main_blueprint
from flask import request, jsonify
from app import db
from sqlalchemy import desc, asc
from app.models import TPRequest
from app.auth import requires_auth
from werkzeug.utils import secure_filename
from geolite2 import geolite2

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@main_blueprint.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
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
    return jsonify({'requests': reqs})


@main_blueprint.route('/createTPRequest', methods=['POST'])
def create_request():
    req = TPRequest(name=request.form['name'],
                    message=request.form['message'],
                    location=extract_location(request))
    db.session.add(req)
    db.session.commit()
    return jsonify({'request': req.json})


@main_blueprint.route('/getDetail', methods=['GET'])
def get_request():
    request_id = request.args.get('id')
    req = TPRequest.query.filter(TPRequest.id == request_id).one_or_none()
    return jsonify({'request': req.json if req else None})


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
            return jsonify({'request': req.json if req else None})


@main_blueprint.route('/install')
@requires_auth
def install():
    db.create_all()
    return 'ok'
