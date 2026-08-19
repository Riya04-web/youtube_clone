from datetime import datetime
from extensions import db


class Download(db.Model):

    __tablename__ = "downloads"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    video_id = db.Column(
        db.Integer,
        db.ForeignKey("videos.id"),
        nullable=False
    )

    download_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
    video = db.relationship(
    "Video"
    )