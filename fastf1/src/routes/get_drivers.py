from flask import Blueprint, jsonify
from datetime import datetime, timezone
import fastf1
import pandas as pd
from collections import defaultdict

drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/f1")

@drivers_bp.route("/get_drivers")
def get_drivers():
    try:
        now = datetime.now(timezone.utc)
        year = datetime.now().year

        schedule = fastf1.get_event_schedule(year, include_testing=False)
        latest_race = None
        latest_race_date = None

        # Find latest completed race
        for _, event in schedule.iterrows():
            race_date_col = "Session5Date"
            if race_date_col in event and pd.notna(event[race_date_col]):
                race_date = event[race_date_col]
                if race_date < now and (latest_race_date is None or race_date > latest_race_date):
                    latest_race = event
                    latest_race_date = race_date

        if latest_race is None:
            # Fallback to previous year if no races found
            year -= 1
            schedule = fastf1.get_event_schedule(year, include_testing=False)
            for _, event in schedule.iterrows():
                race_date_col = "Session5Date"
                if race_date_col in event and pd.notna(event[race_date_col]):
                    race_date = event[race_date_col]
                    if race_date < now and (latest_race_date is None or race_date > latest_race_date):
                        latest_race = event
                        latest_race_date = race_date

            if latest_race is None:
                return jsonify({"error": f"No completed races found for {year} or {year - 1}"}), 404

        # Load race session
        event_round = int(latest_race["RoundNumber"])
        session = fastf1.get_session(year, event_round, "R")
        session.load(telemetry=False, laps=False, weather=False)

        results = session.results
        if results.empty:
            return jsonify({"error": "No results data available"}), 404

        # Group drivers by team with team ID
        teams = defaultdict(lambda: {"drivers": [], "teamId": None})
        for _, row in results.iterrows():
            if pd.notna(row.get("FullName")) and pd.notna(row.get("TeamName")) and pd.notna(row.get("TeamId")):
                teams[row["TeamName"]]["drivers"].append(row["FullName"])
                teams[row["TeamName"]]["teamId"] = row["TeamId"]

        # Transform into list of team objects
        driver_teams = [
            {"team": team, "id": info["teamId"], "drivers": info["drivers"]}
            for team, info in teams.items()
            if info["teamId"] is not None
        ]

        return jsonify(driver_teams)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch latest race drivers: {str(e)}"}), 500