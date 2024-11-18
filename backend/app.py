from flask import Flask, request
from flask_cors import CORS
import db
import json
from datetime import datetime, timedelta
from str_dt import str_to_dt, str_from_dt, hr_min_from_dt


DB = db.DatabaseDriver()

app = Flask(__name__)
CORS(app)

@app.route("/api/players/", methods=["GET"])
def get_players():
    players = DB.get_all_players()
    return json.dumps(players), 200

@app.route("/api/players/", methods=["POST"])
def create_player():
    body = json.loads(request.data)
    first_name = body.get("first_name")
    last_name = body.get("last_name")
    player_id = DB.create_player(first_name, last_name)
    player = DB.get_player_by_id(player_id)
    return json.dumps(player), 200

@app.route("/api/players/<int:player_id>/", methods=["GET"])
def get_player(player_id):
    player = DB.get_player_by_id(player_id)
    if player is None:
        return json.dumps({"error": f"No player with id {player_id}."}), 404
    return json.dumps(player), 200

@app.route("/api/centers/", methods=["GET"])
def get_centers():
    centers = DB.get_all_centers()
    return json.dumps(centers), 200

@app.route("/api/sessions/", methods=["GET"])
def get_sessions():
    sessions = DB.get_all_sessions()
    return json.dumps(sessions), 200

@app.route("/api/sessions/", methods=["POST"])
def create_session():
    body = json.loads(request.data)
    start = body.get("start")
    end = body.get("end")
    center_id = body.get("center_id")
    session_id = DB.create_session(start, end, center_id)
    session = DB.get_session_by_id(session_id)
    return json.dumps(session), 200

@app.route("/api/sessions/<int:session_id>/", methods=["GET"])
def get_session(session_id):
    session = DB.get_session_by_id(session_id)
    if session is None:
        return json.dumps({"error": f"No session with id {session_id}."}), 404
    return json.dumps(session), 200

@app.route("/api/sessions/<int:session_id>/attendances/", methods=["GET"])
def get_session_attendances(session_id):
    session = DB.get_session_by_id(session_id)
    if session is None:
        return json.dumps({"error": f"No session with id {session_id}."}), 404
    attendances = DB.get_attendances_of_session(session_id)
    return json.dumps(attendances), 200

@app.route("/api/sessions/<int:session_id>/signin/<int:player_id>/", methods=["POST"])
def sign_in_player(session_id, player_id):
    session = DB.get_session_by_id(session_id)
    if session is None:
        return json.dumps({"error": f"No session with id {session_id}."}), 404
    player = DB.get_player_by_id(player_id)
    if player is None:
        return json.dumps({"error": f"No player with id {player_id}."}), 404
    attendance = DB.get_session_attendance(session_id, player_id)
    if attendance is not None:
        return json.dumps({"error": f"Player with id {player_id} has already signed in for session with id {session_id}."}), 400

    arrival_dt = datetime.now()
    session_start_dt = str_to_dt(session.get("start"))
    session_end_dt = str_to_dt(session.get("end"))
    #if not session_start_dt - timedelta(minutes=15) <= arrival_dt <= session_end_dt:
    #    return json.dumps({"error": f"Players may sign in 15 min before {hr_min_from_dt(session_start_dt)} until {hr_min_from_dt(session_end_dt)} for session with id {session_id}."}), 400
    arrival_dt = max(session_start_dt, arrival_dt)

    attendance_id = DB.create_session_attendance(session_id, player_id, str_from_dt(arrival_dt))
    attendance = DB.get_session_attendance_by_id(attendance_id)
    return json.dumps(attendance), 200

@app.route("/api/sessions/<int:session_id>/signout/<int:player_id>/", methods=["POST"])
def sign_out_player(session_id, player_id):
    session = DB.get_session_by_id(session_id)
    if session is None:
        return json.dumps({"error": f"No session with id {session_id}."}), 404
    player = DB.get_player_by_id(player_id)
    if player is None:
        return json.dumps({"error": f"No player with id {player_id}."}), 404
    attendance = DB.get_session_attendance(session_id, player_id)
    if attendance is None:
        return json.dumps({"error": f"Player with id {player_id} has not signed in for session with id {session_id}."}), 400

    departure_dt = datetime.now()
    session_end_dt = str_to_dt(session.get("end"))
    departure_dt = min(session_end_dt, departure_dt)

    attendance_id = DB.set_departure_session_attendance(session_id, player_id, str_from_dt(departure_dt))
    attendance = DB.get_session_attendance_by_id(attendance_id)
    return json.dumps(attendance), 200

@app.route("/api/signups/", methods=["POST"])
def signup_court():
    body = json.loads(request.data)
    court_id = body.get("court_id")
    interval_id = body.get("interval_id")
    player_id = body.get("player_id")
    if court_id is None or interval_id is None or player_id is None:
        return json.dumps({"error": "Please provide court_id, interval_id, and player_id."}), 400

    court = DB.get_court_by_id(court_id)
    if court is None:
        return json.dumps({"error": f"No court with id {court_id}."}), 400

    interval = DB.get_interval_by_id(interval_id)
    if interval is None:
        return json.dumps({"error": f"No interval with id {interval_id}."}), 400

    player = DB.get_player_by_id(player_id)
    if player is None:
        return json.dumps({"error": f"No player with id {player_id}."}), 400

    remove = body.get("remove") if body.get("remove") is not None else False

    if remove:
        signup = DB.get_court_signup(interval_id, court_id, player_id)
        if signup is None:
            return json.dumps({"error": f"No existing signup with interval id {interval_id}, court id {court_id}, player id {player_id}."})
        signup_id = DB.remove_court_signup(interval_id, court_id, player_id)
        return json.dumps(signup), 200

    existing_signups = DB.get_signups_of_court(court_id, interval_id)

    if len(existing_signups) == 4:
        return json.dumps({"error": f"There are already 4 players signed up for court id {court_id}, interval id {interval_id}."}), 400
    
    for signup in existing_signups:
        if signup["player_id"] == player_id:
            return json.dumps({"error": f"Player with id {player_id} has already signed up for court id {court_id} in interval {interval_id}."})

    signup_id = DB.create_court_signup(interval_id, court_id, player_id)
    signup = DB.get_court_signup_by_id(signup_id)
    return signup

@app.route("/api/signups/<int:session_id>/past/", methods=["GET"])
def get_past_court_signups(session_id):
    #now = str_from_dt(datetime.now())
    now = "2024-11-06 22:46:00"
    signups = DB.get_past_player_signups_of_session_by_interval_court(session_id, now)
    return json.dumps(signups), 200

@app.route("/api/signups/<int:session_id>/live/", methods=["GET"])
def get_live_court_signups(session_id):
    #now = str_from_dt(datetime.now())
    now = "2024-11-06 22:46:00"
    signups = DB.get_live_player_signups_of_session_by_interval_court(session_id, now)
    return json.dumps(signups), 200

@app.route("/api/signups/<int:interval_id>/<int:court_id>/", methods=["GET"])
def get_court_signups_players(interval_id, court_id):
    signups = DB.get_signups_of_court(court_id, interval_id)
    players = [DB.get_player_by_id(signup["player_id"]) for signup in signups]
    return json.dumps(players), 200

@app.route("/api/signups/<int:session_id>/bank/", methods=["GET"])
def get_court_signups_bank_players(session_id):
    now = "2024-11-06 22:46:00"
    player_ids = DB.get_players_in_bank(session_id, now)
    return json.dumps(player_ids), 200

@app.route("/api/intervals/<int:interval_id>/", methods=["GET"])
def get_interval(interval_id):
    interval = DB.get_interval_by_id(interval_id)
    if interval is None:
        return json.dumps({"error": f"No interval with id {interval_id}."})
    return interval

@app.route("/api/sessiondata/<int:session_id>/", methods=["GET"])
def get_session_data(session_id):
    session = DB.get_session_by_id(session_id)
    center = DB.get_center_by_id(session["center_id"])
    courts = DB.get_courts_of_center(center["id"])
    intervals = DB.get_intervals_of_session(session_id)

    # For bank_players query
    now = "2024-11-06 22:46:00"
    effective_live_interval_id = DB.get_live_interval_id(session_id, now) if DB.get_live_interval_id(session_id, now) \
        else (0 if str_to_dt(now) < str_to_dt(session["start"]) else intervals[-1]["id"] + 1)

    return {
        "sessionId": session_id,
        "centerName": center["name"],
        "liveIntervalId": effective_live_interval_id,
        "intervals": {
            interval["id"]: {
                "id": interval["id"],
                "start": interval["start"],
                "end": interval["end"],
                "courts": {
                    court["id"]: {
                        "id": court["id"],
                        "intervalId": interval["id"],
                        "number": court["number"],
                        "players": [
                            DB.get_player_by_id(signup["player_id"])
                            for signup in DB.get_signups_of_court(court["id"], interval["id"])
                        ]
                    }
                    for court in courts
                }
            }
            for interval in intervals
        },
        "bank_players": DB.get_players_in_bank(session_id, now)
    }

@app.route("/api/v2/sessiondata/<int:session_id>/", methods=["GET"])
def get_session_data_v2(session_id):
    session = DB.get_session_by_id(session_id)
    center = DB.get_center_by_id(session["center_id"])
    courts = DB.get_courts_of_center(center["id"])
    intervals = DB.get_intervals_of_session(session_id)

    # For bank_players query and liveIntervalId calculation
    now = "2024-11-06 22:46:00"
    effective_live_interval_id = DB.get_live_interval_id(session_id, now) if DB.get_live_interval_id(session_id, now) \
        else (0 if str_to_dt(now) < str_to_dt(session["start"]) else intervals[-1]["id"] + 1)

    return {
        "sessionId": session_id,
        "start": session["start"],
        "end": session["end"],
        "centerName": center["name"],
        "liveIntervalId": effective_live_interval_id,
        "intervals": DB.get_intervals_of_session(session_id),
        "courtIds": DB.get_court_ids_of_session(session_id)
    }
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
