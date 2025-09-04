from flask import Blueprint, jsonify
import fastf1
from datetime import datetime
import pandas as pd
from utils import country_to_code, slugify_location

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/f1")


@calendar_bp.route("/get_race_calendar")
def get_race_calendar():
    year = datetime.now().year
    session_names = ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"]
    calendar = []

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        for _, event in schedule.iterrows():
            sessions = []
            for i, session_name in enumerate(session_names, start=1):
                session_date_col = f"Session{i}Date"
                try:
                    if session_date_col in event and not pd.isna(event[session_date_col]):
                        sessions.append({
                            "name": session_name,
                            "date": event[session_date_col].strftime("%b %d"),
                            "time": event[session_date_col].strftime("%H:%M")
                        })
                except Exception:
                    continue  # skip invalid session dates

            if sessions:  # Only include events with at least one valid session
                calendar.append({
                    "round": int(event["RoundNumber"]),
                    "eventName": event["EventName"].replace("Grand Prix", "GP"),
                    "country": event["Country"],
                    "location": event["Location"],
                    "countryCode": country_to_code(event["Country"]),
                    "slug": slugify_location(event["Location"]),
                    "sessions": sessions
                })

        # Sort the calendar by round number
        calendar.sort(key=lambda r: r["round"])

        return jsonify({"year": year, "calendar": calendar})

    except Exception as e:
        return jsonify({"error": f"Failed to fetch race calendar: {str(e)}"}), 500
