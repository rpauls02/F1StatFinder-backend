from flask import Blueprint, jsonify
import fastf1
from datetime import datetime, timezone
import pandas as pd
from utils import country_to_code, slugify_location

next_event_bp = Blueprint("next_event", __name__, url_prefix="/api/f1")


@next_event_bp.route("/get_next_event")
def get_next_event():
    session_names = ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"]
    try:
        now = datetime.now(timezone.utc)
        upcoming_event = None
        year = datetime.now().year

        # Get season schedule
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        # Find the next upcoming race
        for _, event in schedule.iterrows():
            for i in range(1, 6):
                session_date_col = f"Session{i}Date"
                if session_date_col in event and pd.notna(event[session_date_col]):
                    if event[session_date_col] > now:
                        upcoming_event = event
                        break
            if upcoming_event is not None:
                break

        if upcoming_event is None or not isinstance(upcoming_event, pd.Series):
            return jsonify({"error": f"No upcoming race found for {year}"}), 404

        # Prepare sessions info
        sessions = []
        for i, session_name in enumerate(session_names, start=1):
            session_date_col = f"Session{i}Date"
            if session_date_col in upcoming_event and pd.notna(upcoming_event[session_date_col]):
                session_dt = upcoming_event[session_date_col]
                sessions.append({
                    "name": session_name,
                    "date": session_dt.strftime("%B %d"),
                    "time": session_dt.strftime("%H:%M")
                })

        race_info = {
            "eventName": upcoming_event["EventName"].replace("Grand Prix", "GP"),
            "round": int(upcoming_event["RoundNumber"]),
            "country": upcoming_event["Country"],
            "location": upcoming_event["Location"],
            "countryCode": country_to_code(upcoming_event["Country"]),
            "slug": slugify_location(upcoming_event["Location"]),
            "sessions": sessions
        }

        return jsonify(race_info)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch next event: {str(e)}"}), 500
