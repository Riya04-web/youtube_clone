from extensions import db
from datetime import datetime

class VideoReaction(db.Model):
    __tablename__ = "video_reactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    video_id = db.Column(db.Integer, nullable=False)

    reaction_type = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)