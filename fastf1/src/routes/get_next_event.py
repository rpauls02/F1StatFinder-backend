from flask import Blueprint, jsonify
from datetime import datetime, timezone
import pandas as pd
from utils import iso2_country, slugify_location
from cache import get_event_schedule_cached

next_event_bp = Blueprint("next_event", __name__, url_prefix="/api/f1")


@next_event_bp.route("/get_next_event")
def get_next_event():
    try:
        year = datetime.now().year
        now = datetime.now(timezone.utc)

        schedule = get_event_schedule_cached(year, include_testing=False)
        if schedule.empty:
            return jsonify({"error": f"No event schedule found for {year}"}), 404

        # Filter upcoming races and sort
        upcoming_events = schedule[schedule["Session5Date"] > now].sort_values(
            "Session5Date"
        )
        if upcoming_events.empty:
            return jsonify({"error": f"No upcoming race found for {year}"}), 404

        upcoming_event = upcoming_events.iloc[0]

        # Map event type more safely
        format_map = {
            "sprint": "Sprint Event",
            "sprint_shootout": "Sprint Event",
            "sprint_qualifying": "Sprint Event",
            "conventional": "GP Event",
        }
        event_type = format_map.get(
            upcoming_event.get("EventFormat", "conventional"), "GP Event"
        )

        race_date = (
            upcoming_event["Session5Date"].strftime("%d %B %Y")
            if pd.notna(upcoming_event["Session5Date"])
            else None
        )
        race_time = (
            upcoming_event["Session5Date"].strftime("%H:%M %p")
            if pd.notna(upcoming_event["Session5Date"])
            else None
        )

        race_info = {
            "eventName": upcoming_event["EventName"].replace("Grand Prix", "GP", 1),
            "round": int(upcoming_event["RoundNumber"]),
            "country": str(upcoming_event["Country"]),
            "location": str(upcoming_event["Location"]),
            "countryCode": iso2_country(upcoming_event["Country"]) or None,
            "slug": slugify_location(upcoming_event["Location"]),
            "eventType": event_type,
            "raceDate": race_date,
            "raceTime": race_time,
        }

        return jsonify(race_info)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch next event: {str(e)}"}), 500
