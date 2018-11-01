from sqlalchemy.orm import relationship

from insta_pic.extensions import db
from insta_pic.models.base import AuditMixin, BaseMixin


class Comment(db.Model, BaseMixin, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = relationship('Post', back_populates='comments')
