from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph

db = SQLAlchemy()

# User table to store user data
class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # connect to other tables
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "created_at": self.created_at.isoformat()
        }

# Posts table
class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # connect to comments and likes
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "caption": self.caption,
            "created_at": self.created_at.isoformat(),
            "user": self.user.serialize(),
            "comments": [comment.serialize() for comment in self.comments],
            "likes_count": len(self.likes)
        }

# Comments table
class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "user": self.user.serialize()
        }

# Likes table
class Like(db.Model):
    __tablename__ = 'like'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat()
        }

class Follow(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")

    def serialize(self):
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "followed_id": self.followed_id,
            "created_at": self.created_at.isoformat()
        }

def generate_diagram():
    # make diagram
    diagram = """
Instagram DB Model
================

User
----
id (PK)
username (unique)
email (unique)
password
profile_picture
bio
created_at

Post
----
id (PK)
user_id (FK -> User)
image_url
caption
created_at

Comment
-------
id (PK)
user_id (FK -> User)
post_id (FK -> Post)
content
created_at

Like
----
id (PK)
user_id (FK -> User)
post_id (FK -> Post)
created_at
"""
    
    # save text diagram
    with open('diagram.txt', 'w') as f:
        f.write(diagram)
    
    # make png diagram
    engine = create_engine('sqlite:///instagram.db')
    
    # create all tables
    db.metadata.create_all(engine)
    
    # make the diagram
    graph = create_schema_graph(
        engine,
        metadata=db.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir='LR',
        concentrate=False
    )
    graph.write_png('diagram.png')
    print("done!")

if __name__ == '__main__':
    generate_diagram()
