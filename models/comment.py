from extensions import db

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    video_id = db.Column(db.Integer, nullable=False)

    username = db.Column(db.String(100), nullable=False)

    comment = db.Column(db.Text, nullable=False)

    language = db.Column(db.String(30), default="Unknown")
    
    translated_text = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    likes = db.Column(db.Integer, default=0)

    dislikes = db.Column(db.Integer, default=0)

    reports = db.Column(db.Integer, default=0)

    is_flagged = db.Column(db.Boolean, default=False)
    
    show_location = db.Column(
    db.Boolean,
    default=False
)