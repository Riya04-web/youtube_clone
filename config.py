import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/youtube_clone"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Razorpay
    # Keep these as environment variables for deployment.
    RAZORPAY_KEY_ID = os.environ.get(
        "RAZORPAY_KEY_ID"
    )

    RAZORPAY_KEY_SECRET = os.environ.get(
        "RAZORPAY_KEY_SECRET"
    )

    # Gmail / Flask-Mail
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