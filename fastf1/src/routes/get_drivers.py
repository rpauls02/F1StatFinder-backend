from flask import Blueprint, jsonify
from datetime import datetime, timezone
import fastf1
import pandas as pd
from collections import defaultdict
from cache import get_event_schedule_cached

drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/f1")


@drivers_bp.route("/get_drivers")
def get_drivers():
    """
    Fetch and return driver and team information for the latest completed F1 race
    of the current season. Falls back to the second-latest race if needed.
    """
    try:
        year = datetime.now().year
        now = datetime.now(timezone.utc)

        # Fetch schedule
        schedule = get_event_schedule_cached(year, include_testing=False)
        if schedule.empty:
            return jsonify({"error": f"No schedule found for {year}"}), 404

        latest_race = None
        second_latest_race = None
        latest_race_date = None
        second_latest_race_date = None

        # Identify latest and second-latest completed races
        for _, event in schedule.iterrows():
            race_date = event.get("Session5Date")
            if pd.notna(race_date):
                if race_date.tzinfo is None:
                    race_date = race_date.tz_localize("UTC")
                if race_date < now:
                    if latest_race_date is None or race_date > latest_race_date:
                        second_latest_race, second_latest_race_date = latest_race, latest_race_date
                        latest_race, latest_race_date = event, race_date
                    elif second_latest_race_date is None or race_date > second_latest_race_date:
                        second_latest_race, second_latest_race_date = event, race_date

        if latest_race is None:
            return jsonify({"error": f"No completed races found for {year}"}), 404

        # Load race results
        round_number = int(latest_race["RoundNumber"])
        session = fastf1.get_session(year, round_number, "R")
        session.load(telemetry=False, laps=False, weather=False)
        results = session.results

        # Fallback if empty
        if results.empty or results[results["FullName"].notna() & results["TeamName"].notna()].empty:
            if second_latest_race is None:
                return jsonify({"error": "No drivers found in the latest race and no fallback available"}), 404
            round_number = int(second_latest_race["RoundNumber"])
            session = fastf1.get_session(year, round_number, "R")
            session.load(telemetry=False, laps=False, weather=False)
            results = session.results
            if results.empty or results[results["FullName"].notna() & results["TeamName"].notna()].empty:
                return jsonify({"error": "No drivers found in latest or fallback race"}), 404

        # Group drivers by team
        teams = defaultdict(lambda: {"drivers": [], "teamId": None})
        for _, row in results.iterrows():
            if pd.notna(row.get("FullName")) and pd.notna(row.get("TeamName")) and pd.notna(row.get("TeamId")):
                teams[row["TeamName"]]["drivers"].append(row["FullName"].strip())
                teams[row["TeamName"]]["teamId"] = row["TeamId"]

        driver_teams = [
            {"team": team, "id": info["teamId"], "drivers": info["drivers"]}
            for team, info in sorted(teams.items())
            if info["teamId"] is not None
        ]

        if not driver_teams:
            return jsonify({"error": f"No drivers found for {year}"}), 404

        return jsonify(driver_teams)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch latest race drivers: {str(e)}"}), 500
