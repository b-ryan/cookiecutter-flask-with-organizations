from .extensions import db
from sqlalchemy import func


class StandardMixin(object):
    created_at = db.Column(db.DateTime, nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           server_default=func.now(),
                           onupdate=func.current_timestamp())

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        db.session.add(instance)
        if commit:
            db.session.commit()
        return instance

    def update(self, *, commit=True, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
        return self


class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id``
    to any declarative-mapped class."""
    # From Mike Bayer's "Building the app" talk
    # https://speakerdeck.com/zzzeek/building-the-app
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    @classmethod
    def get_by_id(cls, record_id):
        assert(isinstance(record_id, int))
        return cls.query.get(record_id)


def reference_col(tablename, nullable=True, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
