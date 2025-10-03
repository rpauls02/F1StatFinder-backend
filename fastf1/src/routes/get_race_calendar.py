from flask import Blueprint, jsonify
import pandas as pd
from utils import iso2_country, iso3_country, slugify_location
from cache import get_event_schedule_cached

race_calendar_bp = Blueprint("race_calendar", __name__, url_prefix="/api/f1")

@race_calendar_bp.route("/get_race_calendar/<int:year>")
def get_race_calendar(year):
    try:
        # Standard session names
        default_sessions = ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"]

        schedule = get_event_schedule_cached(year, include_testing=False)
        calendar = []

        for _, event in schedule.iterrows():
            sessions = []

            # Pick session labels based on event format
            if str(event.get("EventFormat")).lower() in {"sprint", "sprint_qualifying", "sprint_shootout"}:
                session_names = ["Practice 1", "Qualifying", "Sprint Shootout", "Sprint", "Race"]
            else:
                session_names = default_sessions

            # Build session list
            for i, session_name in enumerate(session_names, start=1):
                for suffix in ["DateUtc", "Date"]:  # try both
                    col = f"Session{i}{suffix}"
                    if col in event and pd.notna(event[col]):
                        dt = event[col]
                        if hasattr(dt, "strftime"):
                            sessions.append({
                                "name": session_name,
                                "date": dt.strftime("%b %d"),
                                "time": dt.strftime("%H:%M"),
                            })
                        break  # found valid column for this session

            if sessions:
                calendar.append({
                    "round": int(event.get("RoundNumber", 0)),
                    "country": str(event.get("Country", "")),
                    "location": str(event.get("Location", "")),
                    "officialEventName": str(event.get("OfficialEventName", "")),
                    "eventName": str(event.get("EventName", "")),
                    "eventDate": event["EventDate"].strftime("%Y-%m-%dT%H:%M:%SZ")
                                 if pd.notna(event.get("EventDate")) and hasattr(event["EventDate"], "strftime")
                                 else None,
                    "eventFormat": str(event.get("EventFormat", "")),
                    "countryCode2": iso2_country(event.get("Country")) or None,
                    "countryCode3": iso3_country(event.get("Country")) or None,
                    "slug": slugify_location(event.get("Location", "")),
                    "sessions": sessions,
                })

        # Sort calendar by round
        calendar.sort(key=lambda r: r["round"])
        return jsonify({"year": year, "calendar": calendar})

    except Exception as e:
        return jsonify({"error": f"Failed to fetch race calendar: {str(e)}"}), 500
