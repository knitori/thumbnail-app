
from . import db


class Thumbnail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    path = db.Column(db.String)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    __table_args = (
        db.Index('url_idx', 'url', unique=True),
        db.Index('width_idx', 'width'),
        db.Index('height_idx', 'height'),
    )
