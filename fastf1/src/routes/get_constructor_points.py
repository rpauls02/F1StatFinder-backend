from flask import Blueprint, jsonify
import pandas as pd
from utils import iso3_country, slugify_location
from cache import (
    get_event_schedule_cached,
    get_race_results_cached,
    get_sprint_results_cached,
)

constructor_points_bp = Blueprint("constructor_points", __name__, url_prefix="/api/f1")


@constructor_points_bp.route("/get_constructor_points/<int:year>")
def get_constructor_points(year):
    """
    Fetch constructor points for a given F1 season, including race and sprint points.
    Adds a 'slug' field for each race based on its location.
    """
    try:
        # Get race schedule
        schedule = get_event_schedule_cached(year, include_testing=False)

        if schedule.empty:
            return jsonify({"error": f"No event schedule found for {year}"}), 404

        rounds = schedule.get("RoundNumber", []).tolist()
        events = schedule.get("EventName", []).tolist()
        countries = schedule.get("Country", []).tolist()
        locations = schedule.get("Location", []).tolist()

        if not rounds or not events or not countries or not locations:
            return jsonify({"error": f"Incomplete schedule data for {year}"}), 500

        country_codes = iso3_country(countries)
        constructor_points = {}

        # Process each race
        for round_number, race_name, country_code, location in zip(
            rounds, events, country_codes, locations
        ):
            race_slug = slugify_location(location)
            weekend_points = {}

            # Fetch race results safely
            try:
                race_data = get_race_results_cached(year, round_number).content
                race_results = race_data[0] if race_data else pd.DataFrame()
            except Exception:
                race_results = pd.DataFrame()

            # Fetch sprint results safely
            try:
                sprint_data = get_sprint_results_cached(year, round_number).content
                sprint_results = sprint_data[0] if sprint_data else pd.DataFrame()
            except Exception:
                sprint_results = pd.DataFrame()

            # Aggregate weekend points
            for df in [race_results, sprint_results]:
                if df.empty:
                    continue
                for _, row in df.iterrows():
                    cid = row.get("constructorId")
                    cname = row.get("constructorName", "Unknown")
                    points = float(row.get("points", 0.0) or 0.0)

                    if cid not in weekend_points:
                        weekend_points[cid] = {
                            "constructorId": cid,
                            "constructor": cname,
                            "weekend_points": 0.0,
                        }
                    weekend_points[cid]["weekend_points"] += points

            # Sort and assign weekend positions
            sorted_weekend = sorted(
                weekend_points.values(), key=lambda x: x["weekend_points"], reverse=True
            )

            for pos, data in enumerate(sorted_weekend, start=1):
                cid = data["constructorId"]
                if cid not in constructor_points:
                    constructor_points[cid] = {
                        "constructorId": cid,
                        "constructor": data["constructor"],
                        "total": 0.0,
                        "races": [],
                    }

                constructor_points[cid]["races"].append({
                    "name": race_name,
                    "slug": race_slug,
                    "country": country_code,
                    "points": data["weekend_points"],
                    "position": pos,
                })
                constructor_points[cid]["total"] += data["weekend_points"]

        if not constructor_points:
            return jsonify({"error": f"No constructor points available for {year}"}), 404

        # Convert to list and sort by total points
        constructors_list = sorted(
            constructor_points.values(), key=lambda c: c["total"], reverse=True
        )

        # Assign championship positions
        for idx, constructor in enumerate(constructors_list, start=1):
            constructor["position"] = idx

        return jsonify(constructors_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor points: {str(e)}"}), 500
