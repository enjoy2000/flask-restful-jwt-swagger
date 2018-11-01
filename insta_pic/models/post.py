from sqlalchemy.orm import relationship

from insta_pic.extensions import db
from insta_pic.models.base import AuditMixin, BaseMixin


class Post(db.Model, BaseMixin, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=False)
    comments = relationship('Comment', back_populates="post")
