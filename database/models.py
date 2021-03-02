from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table

Base = declarative_base()


class IdMixin:
    id = Column(Integer, primary_key=True, autoincrement=True)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
)


class Post(Base, IdMixin, UrlMixin):
    __tablename__ = 'post'
    title = Column(String, nullable=False)
    image = Column(String, unique=False)
    pub_date = Column(String, unique=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author')
    tags = relationship('Tag', secondary=tag_post)
    comments = relationship('Comment')


class Author(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = 'author'
    posts = relationship('Post')


class Tag(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = 'tag'
    posts = relationship('Post', secondary=tag_post)


class Comment(Base,IdMixin):
    __tablename__ = 'comment'
    parent_id = Column(Integer, ForeignKey('comment.id'),nullable=True)
    text = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author')
    post_id = Column(Integer, ForeignKey('post.id'))

    def __init__(self, **kwargs):
        self.parent_id = kwargs["parent_id"]
        self.text = kwargs["body"]
        self.author = kwargs["author"]