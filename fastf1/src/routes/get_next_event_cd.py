from flask import Blueprint, jsonify
from datetime import datetime, timezone
import pandas as pd
from cache import get_event_schedule_cached

# Initialize Blueprint for F1 next event countdown API
next_event_cd_bp = Blueprint("next_event_countdown", __name__, url_prefix="/api/f1")


@next_event_cd_bp.route("/get_next_event_countdown")
def get_next_event_countdown():
    """
    Fetch and return a countdown to the next F1 race in the current season.
    Results are cached for 1 minute to reduce API calls.
    Returns JSON with countdown details (days, hours, minutes, seconds) or an error if no upcoming race is found.
    """
    try:
        year = datetime.now().year
        now = datetime.now(timezone.utc)

        # Fetch schedule
        schedule = get_event_schedule_cached(year, include_testing=False)
        if schedule.empty:
            return jsonify({"error": f"No schedule found for {year}"}), 404

        # Find the next upcoming race
        upcoming_event = (
            schedule[schedule["Session5Date"] > now]
            .sort_values("Session5Date")
            .head(1)
        )

        if upcoming_event.empty:
            return jsonify({"error": f"No upcoming race found for {year}"}), 404

        # Extract race datetime
        race_datetime = upcoming_event.iloc[0]["Session5Date"]
        if pd.isna(race_datetime):
            return jsonify({"error": "Race date missing for upcoming event"}), 500

        # Calculate countdown
        diff = race_datetime - now
        total_seconds = max(int(diff.total_seconds()), 0)

        countdown = {
            "days": total_seconds // (24 * 3600),
            "hours": (total_seconds % (24 * 3600)) // 3600,
            "minutes": (total_seconds % 3600) // 60,
            "seconds": total_seconds % 60,
        }

        return jsonify(countdown)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch next event countdown: {str(e)}"}), 500
