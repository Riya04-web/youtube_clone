from extensions import db
from datetime import datetime

class CommentReaction(db.Model):
    __tablename__ = "comment_reactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    comment_id = db.Column(db.Integer, nullable=False)

    reaction_type = db.Column(db.String(10), nullable=False)   # like / dislike

    created_at = db.Column(db.DateTime, default=datetime.utcnow)