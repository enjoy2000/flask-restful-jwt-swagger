from flask_jwt_extended import get_jwt_identity
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from insta_pic.extensions import db


class BaseMixin(object):
    _repr_hide = ['created_at', 'updated_at']

    def __repr__(self):
        values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys() if n not in self._repr_hide)
        return "%s(%s)" % (self.__class__.__name__, values)

    def save(self):
        db.session.add(self)
        db.session.commit()


class AuditMixin(object):
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def created_by_id(cls):
        return Column(Integer,
                      ForeignKey('user.id', name='fk_%s_created_by_id' % cls.__name__, use_alter=True),
                      # nullable=False,
                      default=_current_user_id_or_none
                      )

    @declared_attr
    def created_by(cls):
        return relationship(
            'User',
            primaryjoin='User.id == %s.created_by_id' % cls.__name__,
            remote_side='User.id'
        )

    @declared_attr
    def updated_by_id(cls):
        return Column(Integer,
                      ForeignKey('user.id', name='fk_%s_updated_by_id' % cls.__name__, use_alter=True),
                      # nullable=False,
                      default=_current_user_id_or_none,
                      onupdate=_current_user_id_or_none
                      )

    @declared_attr
    def updated_by(cls):
        return relationship(
            'User',
            primaryjoin='User.id == %s.updated_by_id' % cls.__name__,
            remote_side='User.id'
        )


def _current_user_id_or_none():
    try:
        return get_jwt_identity()
    except Exception:
        return None
