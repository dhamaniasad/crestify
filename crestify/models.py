# -*- coding: utf-8 -*-
"""Models for Crestify"""
from crestify import app
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType
from flask_security import UserMixin, RoleMixin
from flask_migrate import Migrate, MigrateCommand
from crestify import manager
from sqlalchemy.dialects import postgresql


# Setup SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


class BookmarkQuery(BaseQuery, SearchQueryMixin):
    pass


class Bookmark(db.Model):
    query_class = BookmarkQuery
    __tablename__ = "Bookmarks"
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
