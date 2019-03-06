from . import db
from sqlalchemy.sql import func
from sqlalchemy import event, and_, extract
# from sqlalchemy.ext.declarative import as_declarative
# from sqlalchemy.ext.declarative import declared_attr
import re

#
# @as_declarative()
# class HasImages(object):
#     """Base class which provides automated table name
#         and surrogate primary key column.
#     """
#
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()
#
#
# class Image(db.Model):
#     __tablename__ = 'images'
#     id = db.Column(db.Integer, primary_key=True)
#     image_name = db.Column(db.String(100))
#     imagable_id = db.Column(db.Integer())
#     imagable_type = db.Column(db.String(50))
#     created_at = db.Column(db.DateTime(timezone=True), default=func.now())
#     updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
#
#     @property
#     def parent(self):
#         return getattr(self, 'parent_{}'.format(self.photoable_type))


class User(db.Model):
    """
    Create a Users table, to store user info
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), index=True, unique=True)
    name = db.Column(db.String(100), index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    posts = db.relationship('Post', backref='user', lazy='dynamic')
    # comments = db.relationship('Comment', backref='user', lazy='dynamic')


# class Comment(db.Model):
#     """
#             Create a Comments table to store comments
#         """
#     __tablename__ = "comments"
#
#     id = db.Column(db.Integer, primary_key=True)
#     comment = db.Column(db.String(250))
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
#
#     user = db.relationship('User', backref='comments', lazy='subquery')


post_tags = db.Table('post_tags',
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), nullable=False),
                     db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), nullable=False),
                     db.Column("created_at", db.DateTime(timezone=True), default=func.now())
                     )


class Tag(db.Model):
    """
    Create a Tags table to store tag meta info
    """
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(250))
    category = db.Column(db.String(250))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    post = db.relationship('Post', backref='category', lazy='dynamic')
    # photograph = db.relationship('Photograph', backref='category', lazy='dynamic')

    # posts = db.relationship('Post', secondary=post_tags, lazy='subquery', backref=db.backref('tags', lazy=True))

    def auto_complete_dict(self):
        return dict(id=self.id,
                    tag_name=self.tag_name)

    @staticmethod
    def top_tags(limit=10):
        # "SELECT tags.tag_name AS tags_tag_name, count(posts.id) AS count_1
        #                 FROM posts INNER JOIN post_tags AS post_tags_1 ON posts.id = post_tags_1.post_id
        #                 INNER JOIN tags ON tags.id = post_tags_1.tag_id
        #                 WHERE posts.status IN (%s) GROUP BY tags.id
        #                 LIMIT %s"
        query = db.session.query(Tag.tag_name, Tag.id, db.func.count(Post.id)).\
                           filter(Post.status.in_(['PUBLISHED'])).\
                           join(Post.tags).group_by(Tag.id).order_by(db.func.count(Post.id).desc()).limit(limit)
        return list(query)

    @staticmethod
    def top_categories(limit=5):
        query = db.session.query(Tag.tag_name, Tag.id, db.func.count(Post.id)).\
                           filter(Post.status.in_(['PUBLISHED'])).\
                           join(Post.category).group_by(Tag.id).order_by(db.func.count(Post.id).desc()).limit(limit)
        return list(query)

    @staticmethod
    def top_photo_tags(limit=5):
        query = db.session.query(Tag.tag_name, Tag.id, db.func.count(Photograph.id)).\
                           filter(Photograph.status.in_(['PUBLISHED'])).\
                           join(Photograph.tags).group_by(Tag.id).order_by(db.func.count(Photograph.id).desc()).\
                           limit(limit)
        return list(query)


class Post(db.Model):
    """
    Create a Posts table to store individual blog contents
    """
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(5000))
    title = db.Column(db.String(250))
    href = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    published_at = db.Column(db.DateTime(timezone=True))

    # comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery', backref=db.backref('posts', lazy=True))

    def all_tag_ids(self):
        return ",".join(map(str, [tag.id for tag in self.tags]))

    def all_tags_dict(self):
        return {tag.id: tag.tag_name for tag in self.tags}

    @staticmethod
    def archives():
        query = db.session.query(db.func.count(Post.id),
                                 db.func.MONTHNAME(Post.published_at), db.func.year(Post.published_at)).\
                           filter(Post.status.in_(['PUBLISHED'])).\
                           group_by(db.func.year(Post.published_at),
                                    db.func.month(Post.published_at)
                                    ).\
                           order_by(Post.published_at.desc()).limit(5)
        return list(query)

    @staticmethod
    def generate_href(title):
        href = re.sub('[^a-zA-Z0-9]', ' ', title)
        href = href.strip()
        href = re.sub('  ', '', href)
        href = re.sub(' ', '-', href)
        href = re.sub('--', '-', href)
        href = href.lower()
        return href

# @event.listens_for(HasImages, 'mapper_configured', propagate=True)
# def setup_listener(mapper, class_):
#     name = class_.__name__
#     _type = name.lower()
#     class_.photos = db.relationship(Image,
#                         primaryjoin = and_(
#                                         class_.id == db.foreign(db.remote(Image.imagable_id)),
#                                         Image.imagable_type == _type
#                                      ),
#                         backref = db.backref(
#                                 'parent_{}'.format(type),
#                                 primaryjoin = db.remote(class_.id) == db.foreign(Image.imagable_id)
#                                 )
#                         )
#
#     @event.listens_for(class_.photos, 'append')
#     def append_photo(target, value, initiator):
#         value.imagable_type = _type
#
#     @event.listens_for(class_.photo, 'set')
#     def set_photo(target, value, old_value, initiator):
#         value.photoable_type = _type


photo_tags = db.Table('photo_tags',
                     db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), nullable=False),
                     db.Column('photograph_id', db.Integer, db.ForeignKey('photographs.id'), nullable=False),
                     db.Column("created_at", db.DateTime(timezone=True), default=func.now())
                     )


class Photograph(db.Model):
    __tablename__ = "photographs"
    id = db.Column(db.Integer, primary_key=True)
    photograph_url = db.Column(db.String(1000))
    title = db.Column(db.String(250))
    href = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    published_at = db.Column(db.DateTime(timezone=True))
    capture_date = db.Column(db.DateTime(timezone=True))
    location = db.Column(db.String(250))

    tags = db.relationship('Tag', secondary=photo_tags, lazy='subquery', backref=db.backref('photographs', lazy=True))

    def all_tag_ids(self):
        return ",".join(map(str, [tag.id for tag in self.tags]))

    def tag_names(self):
        return ", ".join(map(str, [tag.tag_name for tag in self.tags]))

    def all_tags_dict(self):
        return {tag.id: tag.tag_name for tag in self.tags}

    @staticmethod
    def archives():
        query = db.session.query(db.func.count(Photograph.id),
                                 db.func.MONTHNAME(Photograph.capture_date), db.func.year(Photograph.capture_date)).\
                           filter(Photograph.status.in_(['PUBLISHED'])).\
                           group_by(db.func.year(Photograph.capture_date),
                                    db.func.month(Photograph.capture_date)
                                    ).\
                           order_by(Photograph.capture_date.desc()).limit(5)
        return list(query)


class ContactRequest(db.Model):
    __tablename__ = "contact_me_requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250))
    message = db.Column(db.String(1000))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
