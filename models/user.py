from extensions import db

class User(db.Model):

    __tablename__ = "users"
    
    is_active = db.Column(db.Boolean, default=True)

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    profile_pic = db.Column(db.String(200), default="default.png")

    plan = db.Column(db.String(20), default="Free")

    
    subscription_status = db.Column(
    db.String(20),
    default="Inactive"
    )

    subscription_start = db.Column(
    db.DateTime
    )

    subscription_end = db.Column(
    db.DateTime
    )

    payment_id = db.Column(
    db.String(100)
    )
    
    invoice_file = db.Column(
    db.String(255)
    )
    
    theme = db.Column(
    db.String(20),
    default=None
)

    last_login = db.Column(
        db.DateTime
    )

    last_city = db.Column(
        db.String(100)
    )

    last_state = db.Column(
        db.String(100)
    )

    last_device = db.Column(
        db.String(255)
    )

    otp = db.Column(db.String(6))
    
    otp_created_at = db.Column(db.DateTime)

    is_verified = db.Column(db.Boolean, default=False)

    profile_pic = db.Column(
        db.String(255),
        default="default.png"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    
    show_location = db.Column(db.Boolean, default=False)

    is_admin = db.Column(db.Boolean, default=False)
    