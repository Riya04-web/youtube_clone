from extensions import db
from models.user import User


class Video(db.Model):

    __tablename__ = "videos"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    title = db.Column(
        db.String(200),
        nullable=False
    )


    description = db.Column(
        db.Text
    )


    filename = db.Column(
        db.String(300),
        nullable=False
    )


    thumbnail = db.Column(
        db.String(300)
    )


    # ⭐ Premium video flag
    is_premium = db.Column(
        db.Boolean,
        default=False
    )


    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )


    views = db.Column(
        db.Integer,
        default=0
    )


    likes = db.Column(
        db.Integer,
        default=0
    )


    dislikes = db.Column(
        db.Integer,
        default=0
    )


    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


    user = db.relationship(
        "User",
        foreign_keys=[uploaded_by]
    )