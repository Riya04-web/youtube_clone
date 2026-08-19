from flask import Flask, render_template, session, redirect, url_for, request
from config import Config
from extensions import db, mail, socketio
from flask_mail import Message

app = Flask(__name__)

app.config.from_object(Config)


socketio.init_app(app)

app.config["PROFILE_UPLOAD_FOLDER"] = "static/profile_pics"

db.init_app(app)
mail.init_app(app)

from models.user import User
from models.video import Video
from routes.auth import auth
from routes.video import video
from routes.watchparty import watchparty
from routes.subscription import subscription

app.register_blueprint(auth)
app.register_blueprint(video)
app.register_blueprint(watchparty)
app.register_blueprint(subscription)


@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    search = request.args.get("search")

    if search:
        videos = Video.query.filter(
            Video.title.contains(search)
        ).all()
    else:
        videos = Video.query.order_by(
            Video.id.desc()
        ).all()

    return render_template(
        "index.html",
        username=session["username"],
        videos=videos
    )

@app.route("/test_email")
def test_email():

    msg = Message(
        subject="🎉 Test Email from YouTube Clone",
        sender=Config.MAIL_USERNAME,
        recipients=["riyashrmaa04@gmail.com"]
    )

    msg.body = """
Congratulations!

Your Flask-Mail configuration is working successfully.

- YouTube Clone
"""

    mail.send(msg)

    return "Email sent successfully!"


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )