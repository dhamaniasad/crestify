# -*- coding: utf-8 -*-
"""Models for Crestify"""
from crestify import app
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_utils.types import TSVectorType
from flask_security import UserMixin, RoleMixin
from flask_migrate import Migrate, MigrateCommand
from crestify import manager
from sqlalchemy.dialects import postgresql

from crestify.services.search import add_to_index, query_index, remove_from_index

# Setup SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page, filters=None):
        ids, total = query_index(cls.__tablename__, expression, page, per_page, filters)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)),
            total,
        )

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


def index_all_bookmarks():
    for bookmark in Bookmark.query.all():
        add_to_index("bookmarks", bookmark)


class Bookmark(SearchableMixin, db.Model):
    __tablename__ = "Bookmarks"
    __searchable__ = [
        "title",
        "description",
        "full_text",
        "user",
        "deleted",
        "tags",
        "main_url",
        "added_on",
    ]
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024), nullable=True)
    description = db.Column(db.String(256))
    main_url = db.Column(db.String(2000))
    added_on = db.Column(db.DateTime())
    user = db.Column(db.Integer, db.ForeignKey("User.id"))
    deleted = db.Column(db.Boolean, default=False)
    search_vector = db.Column(TSVectorType("title", "description"))
    archives = db.relationship("Archive")
    readability_html = db.Column(db.Text, nullable=True)
    tags = db.Column(postgresql.ARRAY(db.String))
    full_text = db.Column(db.Text, nullable=True)
    fulltext_vector = db.Column(TSVectorType("full_text"))


roles_users = db.Table(
    "roles_users",
    db.Column("User_id", db.Integer(), db.ForeignKey("User.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )
    bookmarks_per_page = db.Column(db.Integer, default=20)
    api_key = db.Column(db.String(255), unique=True, nullable=True)


class Archive(db.Model):
    __tablename__ = "Archive"

    ARCHIVE_PENDING = "ARCHIVE_PENDING"
    ARCHIVE_IN_PROGRESS = "ARCHIVE_IN_PROGRESS"
    ARCHIVE_SUCCESSFUL = "ARCHIVE_SUCCESSFUL"
    ARCHIVE_FAILURE = "ARCHIVE_FAILURE"
    ARCHIVE_ERROR = "ARCHIVE_ERROR"

    id = db.Column(db.Integer, primary_key=True)
    web_page = db.Column(db.Integer, db.ForeignKey("Bookmarks.id"))
    service = db.Column(db.String(2048))
    archived_on = db.Column(db.DateTime())
    archive_url = db.Column(db.String(2000))
    status = db.Column(db.String(2000))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255))
    user = db.Column(db.Integer, db.ForeignKey("User.id"))
    count = db.Column(db.Integer, default=0)

    def __init__(self, text, user):
        self.text = text
        self.user = user


class Tab(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    tabs = db.Column(db.PickleType())
    added_on = db.Column(db.DateTime())
    user = db.Column(db.Integer, db.ForeignKey("User.id"))
    title = db.Column(db.String(255))


# Setup event listeners
db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)
