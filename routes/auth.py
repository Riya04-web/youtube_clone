from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from extensions import db, mail
from models.user import User
import random
import re
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from models.download import Download
from models.video import Video
from datetime import datetime
import requests
from zoneinfo import ZoneInfo
from models.comment import Comment


auth = Blueprint("auth", __name__)

def get_ist_theme():
    ist_hour = datetime.now(ZoneInfo("Asia/Kolkata")).hour
    return "light" if 10 <= ist_hour < 12 else "dark"

def check_subscription(user):

    if user.plan == "Premium" and user.subscription_end:

        if datetime.utcnow() > user.subscription_end:

            user.plan = "Free"

            user.subscription_status = "Expired"

            user.subscription_start = None

            user.subscription_end = None

            user.payment_id = None

            db.session.commit()

# ---------------- strong password ----------------
def is_strong_password(password):

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&^#])[A-Za-z\d@$!%*?&^#]{8,}$"

    return re.match(pattern, password)


# ---------------- REGISTER ----------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if not is_strong_password(password):
            flash(
        "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
        "danger"
                )
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.register"))

        otp = str(random.randint(100000, 999999))
        otp_time = datetime.utcnow()

        hashed_password = generate_password_hash(password)

        new_user = User(
    username=username,
    email=email,
    password=hashed_password,
    otp=otp,
    otp_created_at=otp_time,
    is_verified=False
)

        db.session.add(new_user)
        db.session.commit()

        msg = Message(
            subject="Verify your Email",
            recipients=[email]
        )

        msg.body = f"""
Welcome to YouTube Clone!

Your OTP is:

{otp}

Enter this OTP to verify your account.
"""

        mail.send(msg)

        return render_template(
    "verify_email.html",
    email=email,
    message="OTP has been sent to your email.",
    remaining_time=60
)

    return render_template("register.html")


# ---------------- VERIFY EMAIL ----------------

@auth.route("/verify_email/<email>", methods=["GET", "POST"])
def verify_email(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("auth.register"))

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if entered_otp == user.otp:

            user.is_verified = True
            user.otp = None

            db.session.commit()

            flash("Email verified successfully! Please login.", "success")

            return redirect(url_for("auth.login"))

        else:

            flash("Invalid OTP. Please try again.", "danger")

    
    from datetime import timedelta

    remaining_time = 0

    if user.otp_created_at:

        elapsed = (datetime.utcnow() - user.otp_created_at).total_seconds()

        remaining_time = max(0, 60 - int(elapsed)) 
    
    print("Remaining Time =", remaining_time)
    
    return render_template(
    "verify_email.html",
    email=email,
    remaining_time=remaining_time
)


@auth.route("/resend_otp/<email>")
def resend_otp(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("auth.register"))

    otp = str(random.randint(100000, 999999))

    user.otp = otp
    user.otp_created_at = datetime.utcnow()
    db.session.commit()

    msg = Message(
        subject="Your New OTP",
        recipients=[email]
    )

    msg.body = f"""
Hello,

Your new OTP is:

{otp}

Use this OTP to verify your account.
"""

    mail.send(msg)

    flash("A new OTP has been sent to your email.", "success")

    return redirect(url_for("auth.verify_email", email=email))

# ---------------- LOGIN ----------------

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        login_type = request.form.get("login_type")
    
        
        
        user = User.query.filter_by(email=email).first()

        
        if not user:
            flash("User not found!", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect Password!", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account has been deactivated.", "danger")
            return redirect(url_for("auth.login"))
        
        if not user.is_verified:
            flash("Please verify your email first.", "warning")
            return redirect(
    url_for("auth.verify_login_otp", email=user.email)
)

        current_device = request.headers.get("User-Agent")

        ip = request.remote_addr

        try:

            response = requests.get(
                f"http://ip-api.com/json/{ip}",
                timeout=5
            ).json()

            current_city = response.get("city", "")
            current_state = response.get("regionName", "")

        except:

            current_city = ""
            current_state = ""

                # Check if device or location has changed
        new_login = False

        if user.last_device and user.last_device != current_device:
            new_login = True

        if user.last_city and user.last_city != current_city:
            new_login = True

        if user.last_state and user.last_state != current_state:
            new_login = True

        if new_login:

            import random

            otp = str(random.randint(100000, 999999))

            user.otp = otp
            user.otp_created_at = datetime.utcnow()

            db.session.commit()

            msg = Message(
                subject="Login Verification OTP",
                recipients=[user.email]
            )

            msg.body = f"""
Hello {user.username},

A login from a new device or location was detected.

City: {current_city}
State: {current_state}

Your OTP is:

{otp}

If this wasn't you, please change your password immediately.
"""

            mail.send(msg)

            flash(
                "New device/location detected. OTP has been sent to your email.",
                "warning"
            )

            return redirect(
                url_for("auth.verify_login_otp", email=user.email)
            )
            
                    # Automatic theme selection (based on IST)
        # Automatic theme selection only if user has no saved theme
        if not user.theme:
            user.theme = get_ist_theme()
            
        # Save login information
        user.last_device = current_device
        user.last_city = current_city
        user.last_state = current_state
        user.last_login = datetime.utcnow()

        db.session.commit()

        # Login session
        session["user_id"] = user.id
        session["username"] = user.username
        session["profile_pic"] = user.profile_pic
        session["plan"] = user.plan
        session["theme"] = user.theme

        flash("Login successful!", "success")

        if login_type == "admin":

            print("ADMIN SELECTED")

            if user.is_admin:
                print("GOING TO ADMIN DASHBOARD")
                return redirect(url_for("auth.admin_dashboard"))

            session.clear()
            flash("You are not an administrator!", "danger")
            return redirect(url_for("auth.login"))

        print("GOING TO HOME")
        return redirect(url_for("home"))

    return render_template("login.html")

@auth.route("/verify_login_otp/<email>", methods=["GET", "POST"])
def verify_login_otp(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        entered_otp = request.form["otp"]

        if entered_otp != user.otp:
            flash("Invalid OTP.", "danger")
            return redirect(url_for("auth.verify_login_otp", email=email))

        user.otp = None

        current_device = request.headers.get("User-Agent")

        ip = request.remote_addr

        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip}",
                timeout=5
            ).json()

            current_city = response.get("city", "")
            current_state = response.get("regionName", "")

        except:
            current_city = ""
            current_state = ""

        # Automatic theme selection (based on IST)
        if not user.theme:
            user.theme = get_ist_theme()

        user.last_device = current_device
        user.last_city = current_city
        user.last_state = current_state
        user.last_login = datetime.utcnow()

        db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username
        session["profile_pic"] = user.profile_pic
        session["plan"] = user.plan
        session["theme"] = user.theme

        flash("Login successful!", "success")

        return redirect(url_for("home"))

    return render_template(
        "verify_login_otp.html",
        email=email
    )

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with this email.", "danger")
            return redirect(url_for("auth.forgot_password"))

        otp = str(random.randint(100000,999999))

        user.otp = otp
        user.otp_created_at = datetime.utcnow()

        db.session.commit()

        msg = Message(
            subject="Reset Your Password",
            recipients=[email]
        )

        msg.body = f"""
Hello,

Your password reset OTP is:

{otp}

Use this OTP to reset your password.

If you didn't request this, simply ignore this email.
"""

        mail.send(msg)

        return redirect(url_for("auth.reset_password", email=email))

    return render_template("forgot_password.html")

@auth.route("/reset_password/<email>", methods=["GET", "POST"])
def reset_password(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":

        entered_otp = request.form["otp"]
        new_password = request.form["password"]
        if not is_strong_password(new_password):
            flash(
        "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
        "danger"
                )
            return redirect(url_for("auth.reset_password", email=email))

        if entered_otp != user.otp:
            flash("Invalid OTP!", "danger")
            return redirect(url_for("auth.reset_password", email=email))

        user.password = generate_password_hash(new_password)
        user.otp = None

        db.session.commit()

        flash("Password reset successfully! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template(
        "reset_password.html",
        email=email
    )

@auth.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        username = request.form["username"]
        user.username = username

        # Upload profile picture
        if "profile_pic" in request.files:

            file = request.files["profile_pic"]

            if file.filename != "":

                filename = secure_filename(file.filename)

                file.save(os.path.join("static/profile_pics", filename))

                user.profile_pic = filename
                
                session["profile_pic"] = filename

        db.session.commit()

        session["username"] = username

        flash("Profile updated successfully!", "success")

        return redirect(url_for("auth.profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )



@auth.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    check_subscription(user)


    downloads = Download.query.filter_by(
        user_id=user.id
    ).order_by(
        Download.download_date.desc()
    ).all()


    return render_template(
        "profile.html",
        user=user,
        downloads=downloads
    )

@auth.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Check current password
        if not check_password_hash(user.password, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("auth.change_password"))

        # Check new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("auth.change_password"))

        # Strong password validation
        if not is_strong_password(new_password):
            flash(
                "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
                "danger"
            )
            return redirect(url_for("auth.change_password"))

        # Prevent using the same password again
        if check_password_hash(user.password, new_password):
            flash("New password cannot be the same as your current password.", "warning")
            return redirect(url_for("auth.change_password"))

        # Save new password
        user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password changed successfully!", "success")

        return render_template("change_password.html")

    return render_template("change_password.html")

@auth.route("/subscription")
def subscription():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    return render_template(
        "subscription.html",
        user=user
    )

@auth.route("/payment")
def payment():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    check_subscription(user)

    return render_template(
        "payment.html",
        user=user
    )

@auth.route("/upgrade")
def upgrade():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    user.plan = "Premium"

    user.subscription_status = "Active"

    user.subscription_start = datetime.utcnow()

    user.subscription_end = datetime.utcnow() + timedelta(days=30)

    user.payment_id = "TEST_PAYMENT"

    db.session.commit()

    flash(
        "Congratulations! Your Premium subscription is activated.",
        "success"
    )

    return redirect(url_for("auth.payment"))

@auth.route("/change_theme", methods=["POST"])
def change_theme():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    selected_theme = request.form["theme"]

    user.theme = selected_theme

    db.session.commit()

    session["theme"] = selected_theme

    flash("Theme updated successfully!", "success")

    return redirect(url_for("auth.profile"))

@auth.route("/change_location_visibility", methods=["POST"])
def change_location_visibility():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    user.show_location = "show_location" in request.form

    db.session.commit()

    flash("Location privacy setting updated!", "success")

    return redirect(url_for("auth.profile"))

# ---------------- LOGOUT ----------------

@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))

@auth.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    reported_comments = Comment.query.filter_by(
        is_flagged=True
    ).order_by(
        Comment.reports.desc()
    ).all()
    
    total_users = User.query.count()

    total_videos = Video.query.count()

    total_comments = Comment.query.count()

    total_reports = Comment.query.filter_by(
        is_flagged=True
    ).count()

    return render_template(
    "admin_dashboard.html",
    user=user,
    reported_comments=reported_comments,
    total_users=total_users,
    total_videos=total_videos,
    total_comments=total_comments,
    total_reports=total_reports
)
    
@auth.route("/admin/users")
def manage_users():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if not user.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    users = User.query.order_by(User.id.desc()).all()

    return render_template(
        "admin_users.html",
        user=user,
        users=users
    )

@auth.route("/admin/users/toggle/<int:user_id>")
def toggle_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    admin = User.query.get(session["user_id"])

    if not admin.is_admin:
        flash("Access Denied!", "danger")
        return redirect(url_for("home"))

    user = User.query.get_or_404(user_id)

    # Prevent admin from deactivating themselves
    if user.id == admin.id:
        flash("You cannot deactivate your own admin account!", "warning")
        return redirect(url_for("auth.manage_users"))

    user.is_active = not user.is_active

    db.session.commit()

    if user.is_active:
        flash(f"{user.username} has been activated.", "success")
    else:
        flash(f"{user.username} has been deactivated.", "warning")

    return redirect(url_for("auth.manage_users"))