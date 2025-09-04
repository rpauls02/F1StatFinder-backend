from flask import Blueprint, jsonify
import fastf1
from datetime import datetime, timezone
import pandas as pd

next_event_cd_bp = Blueprint("next_event_countdown", __name__, url_prefix="/api/f1")


@next_event_cd_bp.route("/get_next_event_countdown")
def get_next_event_countdown():
    try:
        year = datetime.now().year
        now = datetime.now(timezone.utc)
        upcoming_event = None

        # Get season schedule
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        # Find the next upcoming race
        for _, event in schedule.iterrows():
            race_date_col = "Session5Date"  # Race session
            if race_date_col in event and pd.notna(event[race_date_col]):
                if event[race_date_col] > now:
                    upcoming_event = event
                    break

        if upcoming_event is None or not isinstance(upcoming_event, pd.Series):
            return jsonify({"error": f"No upcoming race found for {year}"}), 404

        # Calculate countdown
        race_datetime = upcoming_event["Session5Date"]
        diff = race_datetime - now
        total_seconds = int(diff.total_seconds())

        countdown = {
            "days": max(total_seconds // (24 * 3600), 0),
            "hours": max((total_seconds % (24 * 3600)) // 3600, 0),
            "minutes": max((total_seconds % 3600) // 60, 0),
            "seconds": max(total_seconds % 60, 0),
        }

        return jsonify(countdown)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch next event countdown: {str(e)}"}), 500
