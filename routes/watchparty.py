from flask import Blueprint, render_template, redirect, url_for, session, request
import uuid

from flask_socketio import join_room, leave_room, emit
from extensions import socketio


watchparty = Blueprint("watchparty", __name__)


rooms = {}
participants = {}


# ---------------- JOIN SOCKET ----------------

@socketio.on("join")
def on_join(data):

    room = data["room"]
    username = data["username"]

    join_room(room)

    if room not in participants:
        participants[room] = []

    if username not in participants[room]:
        participants[room].append(username)

    emit(
        "update_participants",
        {
            "participants": participants[room],
            "host": rooms.get(room, {}).get("host")
        },
        room=room
    )


    emit(
        "message",
        {
            "msg": f"{username} joined the watch party 🎉"
        },
        room=room
    )



# ---------------- LEAVE ----------------

@socketio.on("leave")
def on_leave(data):

    room = data["room"]
    username = data["username"]

    leave_room(room)

    if room in participants:

        if username in participants[room]:
            participants[room].remove(username)


        emit(
            "update_participants",
            {
                "participants": participants[room],
                "host": rooms.get(room, {}).get("host")
            },
            room=room
        )


    emit(
        "message",
        {
            "msg": f"{username} left the watch party."
        },
        room=room
    )



# ---------------- CHAT ----------------

@socketio.on("send_message")
def send_message(data):

    emit(
        "receive_message",
        {
            "username": data["username"],
            "message": data["message"]
        },
        room=data["room"]
    )



# ---------------- VIDEO SYNC ----------------

@socketio.on("play_video")
def play_video(data):

    emit(
        "play_video",
        {
            "currentTime": data["currentTime"]
        },
        room=data["room"],
        include_self=False
    )


@socketio.on("pause_video")
def pause_video(data):

    emit(
        "pause_video",
        {
            "currentTime": data["currentTime"]
        },
        room=data["room"],
        include_self=False
    )


@socketio.on("seek_video")
def seek_video(data):

    emit(
        "seek_video",
        {
            "currentTime": data["currentTime"]
        },
        room=data["room"],
        include_self=False
    )



# ---------------- WATCH PARTY HOME ----------------

@watchparty.route("/watchparty/<int:video_id>")
def watchparty_home(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "watchparty_home.html",
        video_id=video_id
    )


# ---------------- CREATE ROOM ----------------

@watchparty.route("/create_room/<int:video_id>")
def create_room(video_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    room_id = str(uuid.uuid4())[:8]


    rooms[room_id] = {

        "host": session["username"],
        "video_id": video_id

    }


    return redirect(
        url_for(
            "watchparty.room",
            room_id=room_id
        )
    )



# ---------------- JOIN ROOM PAGE ----------------

@watchparty.route("/join_room", methods=["GET","POST"])
def join_room_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    if request.method == "POST":

        room_id = request.form["room_id"]


        if room_id in rooms:

            return redirect(
                url_for(
                    "watchparty.room",
                    room_id=room_id
                )
            )


        else:

            return "Room does not exist"


    return render_template(
        "join_room.html"
    )



# ---------------- ROOM ----------------

@watchparty.route("/room/<room_id>")
def room(room_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    room_data = rooms.get(room_id)


    if not room_data:
        return "Room does not exist"


    video_id = room_data["video_id"]


    from models.video import Video

    video = Video.query.get(video_id)


    print("VIDEO OBJECT:", video)

    if video:
        print("VIDEO FILE:", video.filename)


    return render_template(
        "watchparty_room.html",
        room_id=room_id,
        username=session["username"],
        host=room_data["host"],
        video=video,
        join_link=request.host_url + "room/" + room_id
    )

# ---------------- WEBRTC ----------------

@socketio.on("offer")
def offer(data):

    emit(
        "offer",
        data,
        room=data["room"],
        include_self=False
    )


@socketio.on("answer")
def answer(data):

    emit(
        "answer",
        data,
        room=data["room"],
        include_self=False
    )


@socketio.on("ice_candidate")
def ice_candidate(data):

    emit(
        "ice_candidate",
        data,
        room=data["room"],
        include_self=False
    )