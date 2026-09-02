from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO
import os

db = SQLAlchemy()
mail = Mail()

socketio = SocketIO(
    async_mode="threading",
    message_queue=os.environ.get("REDIS_URL")
)