import re
import time
from deep_translator import GoogleTranslator
from langdetect import detect
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    send_from_directory
)

from werkzeug.utils import secure_filename
from extensions import db
from models.video import Video
from models.comment import Comment
from models.user import User
from models.download import Download
from models.comment_reaction import CommentReaction
from models.video_reaction import VideoReaction
from config import Config

import os
import cloudinary
import cloudinary.uploader
from datetime import datetime
from zoneinfo import ZoneInfo

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

video = Blueprint("video", __name__)

@video.route("/cloudinary_signature")
def cloudinary_signature():

    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    timestamp = int(time.time())

    signature = cloudinary.utils.api_sign_request(
        {
            "timestamp": timestamp
        },
        cloudinary.config().api_secret
    )

    return {
        "signature": signature,
        "timestamp": timestamp,
        "api_key": cloudinary.config().api_key,
        "cloud_name": cloudinary.config().cloud_name
    }

UPLOAD_FOLDER = "static/uploads"
BAD_WORDS = [
    "idiot",
    "stupid",
    "fool",
    "hate",
    "damn",
    "hell"
]


# ===========================
# WATCH VIDEO
# ===========================

@video.route("/watch/<int:video_id>", methods=["GET", "POST"])
def watch_video(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    video_data = Video.query.get_or_404(video_id)

    print("Video:", video_data.title)
    print("Premium:", video_data.is_premium)
    
    user = User.query.get(session["user_id"])

    # Premium restriction
    if video_data.is_premium:

        allowed_plans = [
            "bronze",
            "silver",
            "gold"
        ]

        if user.plan.lower() not in allowed_plans:

            

            return redirect(
                url_for("subscription.subscription_page")
            )

    if request.method == "POST":

        comment_text = request.form["comment"].strip()

# Empty comment
        if not comment_text:
            flash("Comment cannot be empty.", "danger")
            return redirect(url_for("video.watch_video", video_id=video_id))

# Abusive words
        for word in BAD_WORDS:
            if word in comment_text.lower():
                flash("Your comment contains inappropriate language.", "danger")
                return redirect(url_for("video.watch_video", video_id=video_id))

# Repeated special characters (!!!!!!, ??????, $$$$$)
        if re.fullmatch(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~]{4,}", comment_text):
            flash("Please avoid posting only special characters.", "danger")
            return redirect(url_for("video.watch_video", video_id=video_id))

# Same character repeated (aaaaaaa, !!!!!, 111111)
        if re.search(r"(.)\1{5,}", comment_text):
            flash("Spam comment detected.", "danger")
            return redirect(url_for("video.watch_video", video_id=video_id))

        try:
            if len(comment_text.split()) <= 2:
                detected_language = "en"
            else:
                detected_language = detect(comment_text)
        except:
                detected_language = "en"

        user = User.query.get(session["user_id"])

        new_comment = Comment(
    video_id=video_id,
    username=session["username"],
    comment=comment_text,
    language=detected_language,
    show_location=user.show_location,
    created_at=datetime.utcnow()
)

        db.session.add(new_comment)
        db.session.commit()

        flash("Comment added successfully!", "success")

        return redirect(
            url_for("video.watch_video", video_id=video_id)
        )

    comments = Comment.query.filter_by(
        video_id=video_id
    ).order_by(
        Comment.id.desc()
    ).all()

    for comment in comments:

        # Get comment author
        comment.author = User.query.filter_by(
            username=comment.username
    ).first()

    # Convert database time (UTC) to IST
        if comment.created_at:
            comment.created_at_ist = comment.created_at.replace(
                tzinfo=ZoneInfo("UTC")
            ).astimezone(
                ZoneInfo("Asia/Kolkata")
            )
        else:
            comment.created_at_ist = None
    
    # ===========================
# NEXT VIDEO
# ===========================

    next_video = Video.query.filter(
    Video.id > video_id
    ).order_by(
    Video.id.asc()
    ).first()

# If this is the last video, start again from the first video
    if not next_video:
        next_video = Video.query.order_by(Video.id.asc()).first()

    return render_template(
    "watch.html",
    video=video_data,
    comments=comments,
    user=user,
    next_video=next_video
)


# ===========================
# LIKE VIDEO
# ===========================

@video.route("/like/<int:video_id>")
def like_video(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    video_data = Video.query.get_or_404(video_id)

    reaction = VideoReaction.query.filter_by(
        user_id=session["user_id"],
        video_id=video_id
    ).first()

    # Already liked
    if reaction and reaction.reaction_type == "like":

        flash("You already liked this video.", "info")

    # Change dislike to like
    elif reaction and reaction.reaction_type == "dislike":

        reaction.reaction_type = "like"

        video_data.dislikes -= 1
        video_data.likes += 1

        db.session.commit()

        flash("Reaction changed to Like.", "success")

    # First reaction
    else:

        new_reaction = VideoReaction(
            user_id=session["user_id"],
            video_id=video_id,
            reaction_type="like"
        )

        db.session.add(new_reaction)

        video_data.likes += 1

        db.session.commit()

        flash("Video liked!", "success")

    return redirect(
        url_for("video.watch_video", video_id=video_id)
    )


# ===========================
# DISLIKE VIDEO
# ===========================

@video.route("/dislike/<int:video_id>")
def dislike_video(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    video_data = Video.query.get_or_404(video_id)

    reaction = VideoReaction.query.filter_by(
        user_id=session["user_id"],
        video_id=video_id
    ).first()

    # Already disliked
    if reaction and reaction.reaction_type == "dislike":

        flash("You already disliked this video.", "info")

    # Change like to dislike
    elif reaction and reaction.reaction_type == "like":

        reaction.reaction_type = "dislike"

        video_data.likes -= 1
        video_data.dislikes += 1

        db.session.commit()

        flash("Reaction changed to Dislike.", "success")

    # First reaction
    else:

        new_reaction = VideoReaction(
            user_id=session["user_id"],
            video_id=video_id,
            reaction_type="dislike"
        )

        db.session.add(new_reaction)

        video_data.dislikes += 1

        db.session.commit()

        flash("Video disliked!", "success")

    return redirect(
        url_for("video.watch_video", video_id=video_id)
    )

# ===========================
# DELETE COMMENT
# ===========================

@video.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    if comment.username != session["username"]:

        flash("You cannot delete this comment.", "danger")
        return redirect(
            url_for(
                "video.watch_video",
                video_id=comment.video_id
            )
        )

    video_id = comment.video_id

    db.session.delete(comment)

    db.session.commit()

    flash("Comment deleted successfully.", "success")

    return redirect(
        url_for(
            "video.watch_video",
            video_id=video_id
        )
    )

@video.route("/comment_like/<int:comment_id>")
def comment_like(comment_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    comment = Comment.query.get_or_404(comment_id)

    reaction = CommentReaction.query.filter_by(
        user_id=session["user_id"],
        comment_id=comment_id
    ).first()

    # Already liked
    if reaction and reaction.reaction_type == "like":

        flash("You already liked this comment.", "info")

    # Change dislike to like
    elif reaction and reaction.reaction_type == "dislike":

        reaction.reaction_type = "like"

        comment.dislikes -= 1
        comment.likes += 1

        db.session.commit()

        flash("Reaction changed to Like.", "success")

    # First time like
    else:

        new_reaction = CommentReaction(
            user_id=session["user_id"],
            comment_id=comment_id,
            reaction_type="like"
        )

        db.session.add(new_reaction)

        comment.likes += 1

        db.session.commit()

        flash("Comment liked!", "success")

    return redirect(
        url_for("video.watch_video", video_id=comment.video_id)
    )


@video.route("/comment_dislike/<int:comment_id>")
def comment_dislike(comment_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    comment = Comment.query.get_or_404(comment_id)

    reaction = CommentReaction.query.filter_by(
        user_id=session["user_id"],
        comment_id=comment_id
    ).first()

    # Already disliked
    if reaction and reaction.reaction_type == "dislike":

        flash("You already disliked this comment.", "info")

    # Change like to dislike
    elif reaction and reaction.reaction_type == "like":

        reaction.reaction_type = "dislike"

        comment.likes -= 1
        comment.dislikes += 1

        db.session.commit()

        flash("Reaction changed to Dislike.", "success")

    # First time dislike
    else:

        new_reaction = CommentReaction(
            user_id=session["user_id"],
            comment_id=comment_id,
            reaction_type="dislike"
        )

        db.session.add(new_reaction)

        comment.dislikes += 1

        db.session.commit()

        flash("Comment disliked!", "success")

    return redirect(
        url_for("video.watch_video", video_id=comment.video_id)
    )

@video.route("/translate_comment/<int:comment_id>")
def translate_comment(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    target_lang = request.args.get("target_lang", "en")

    translated = GoogleTranslator(
        source="auto",
        target=target_lang
    ).translate(comment.comment)

    comment.translated_text = translated

    db.session.commit()

    return redirect(
        url_for(
            "video.watch_video",
            video_id=comment.video_id
        )
    )

@video.route("/comment_report/<int:comment_id>")
def comment_report(comment_id):

    comment = Comment.query.get_or_404(comment_id)

    comment.reports += 1

    if comment.reports >= 3:
        comment.is_flagged = True

    db.session.commit()

    flash("Comment reported successfully.", "warning")

    return redirect(url_for("video.watch_video", video_id=comment.video_id))

# ===========================
# UPLOAD VIDEO
# ===========================
# ===========================
# UPLOAD VIDEO
# ===========================

@video.route("/upload", methods=["GET", "POST"])
def upload_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")

        video_url = request.form.get("video_url")
        thumbnail_url = request.form.get("thumbnail_url")

        premium = True if request.form.get("premium") else False

        # Make sure Cloudinary URLs were received
        if not video_url or not thumbnail_url:

            flash(
                "Video and thumbnail upload failed.",
                "danger"
            )

            return redirect(
                url_for("video.upload_page")
            )

        # Save database record
        new_video = Video(
            title=title,
            description=description,
            filename=video_url,
            thumbnail=thumbnail_url,
            is_premium=premium,
            uploaded_by=session["user_id"]
        )

        db.session.add(new_video)
        db.session.commit()

        flash(
            "Video uploaded successfully!",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("upload.html")


# ===========================
# DOWNLOAD VIDEO
# ===========================

@video.route("/download/<int:video_id>")
def download_video(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    video_data = Video.query.get_or_404(video_id)

    user = User.query.get(session["user_id"])

    today = datetime.utcnow().date()

    downloads_today = Download.query.filter(

        Download.user_id == user.id,

        db.func.date(Download.download_date) == today

    ).count()

    plan_limits = {

        "free": 1,

        "bronze": 5,

        "silver": 15,

        "gold": 999999

    }

    download_limit = plan_limits.get(

        user.plan.lower(),

        1

    )

    if downloads_today >= download_limit:

        flash(

            f"{user.plan} users can download only {download_limit} videos per day.",

            "danger"

        )

        return redirect(

            url_for(

                "video.watch_video",

                video_id=video_id

            )

        )

    download = Download(

        user_id=user.id,

        video_id=video_id

    )

    db.session.add(download)

    db.session.commit()

    download_url = video_data.filename.replace(
    "/upload/",
    "/upload/fl_attachment/"
)

    return redirect(download_url)