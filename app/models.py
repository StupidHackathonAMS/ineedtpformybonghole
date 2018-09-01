import time
from app import db


def epoch():
    return int(time.time())


class TPRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    createdAt = db.Column(db.Integer, nullable=False, default=epoch)
    fulfilledAt = db.Column(db.Integer, default=None)
    img_url = db.Column(db.String(200), default=None)

    @property
    def json(self):
        return {'id': self.id,
                'name': self.name,
                'message': self.message,
                'location': self.location,
                'createdAt': self.createdAt,
                'fullfilledAt': self.fulfilledAt,
                'img_url': self.img_url}
