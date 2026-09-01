import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key"
    )

    # ================= DATABASE =================

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:

        # Make sure mysql:// uses PyMySQL
        if DATABASE_URL.startswith("mysql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "mysql://",
                "mysql+pymysql://",
                1
            )

        # Remove query parameters such as ssl-mode
        DATABASE_URL = DATABASE_URL.split("?")[0]

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

        SQLALCHEMY_ENGINE_OPTIONS = {}

    else:

        SQLALCHEMY_DATABASE_URI = (
            "mysql+pymysql://root:@localhost/youtube_clone"
        )

        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # ================= RAZORPAY =================

    RAZORPAY_KEY_ID = os.environ.get(
        "RAZORPAY_KEY_ID"
    )

    RAZORPAY_KEY_SECRET = os.environ.get(
        "RAZORPAY_KEY_SECRET"
    )


    # ================= GMAIL =================

    MAIL_SERVER = "smtp.gmail.com"

    MAIL_PORT = 587

    MAIL_USE_TLS = True

    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_USERNAME"
    )
    
        # ================= CLOUDINARY =================

    CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL")

    CLOUDINARY_CLOUD_NAME = os.environ.get(
        "CLOUDINARY_CLOUD_NAME"
    )

    CLOUDINARY_API_KEY = os.environ.get(
        "CLOUDINARY_API_KEY"
    )

    CLOUDINARY_API_SECRET = os.environ.get(
        "CLOUDINARY_API_SECRET"
    )
