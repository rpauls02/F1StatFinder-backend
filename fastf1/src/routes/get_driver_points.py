from flask import Blueprint, jsonify
import pandas as pd
from utils import iso3_country, slugify_location
from cache import get_event_schedule_cached, get_race_results_cached, get_sprint_results_cached

driver_points_bp = Blueprint("driver_points", __name__, url_prefix="/api/f1")

@driver_points_bp.route("/get_driver_points/<int:year>")
def get_driver_points(year):
    """
    Fetch driver points for a given F1 season, including race and sprint points.
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
        driver_points = {}

        # Process each race
        for round_number, race_name, country_code, location in zip(rounds, events, country_codes, locations):
            race_slug = slugify_location(location)
            weekend_points = {}

            # Fetch race results safely
            try:
                race_results = get_race_results_cached(year, round_number).content[0]
            except Exception:
                race_results = pd.DataFrame()

            # Fetch sprint results safely
            try:
                sprint_results = get_sprint_results_cached(year, round_number).content[0]
            except Exception:
                sprint_results = pd.DataFrame()

            # Aggregate points for the weekend
            for df in [race_results, sprint_results]:
                if df.empty:
                    continue
                for _, row in df.iterrows():
                    d_id = row.get("driverId")
                    if not d_id:
                        continue

                    name = f"{row.get('givenName', '')} {row.get('familyName', '')}".strip() or "Unknown"
                    constructor = row.get("constructorName", "Unknown")
                    points = float(row.get("points", 0.0) or 0.0)

                    if d_id not in weekend_points:
                        weekend_points[d_id] = {
                            "driverId": d_id,
                            "name": name,
                            "constructor": constructor,
                            "weekend_points": 0.0
                        }
                    weekend_points[d_id]["weekend_points"] += points

            # Sort and assign weekend positions
            sorted_weekend = sorted(weekend_points.values(), key=lambda x: x["weekend_points"], reverse=True)
            for pos, data in enumerate(sorted_weekend, start=1):
                d_id = data["driverId"]
                if d_id not in driver_points:
                    driver_points[d_id] = {
                        "driverId": d_id,
                        "name": data["name"],
                        "constructor": data["constructor"],
                        "total": 0.0,
                        "races": []
                    }

                driver_points[d_id]["races"].append({
                    "name": race_name,
                    "slug": race_slug,
                    "country": country_code,
                    "points": data["weekend_points"],
                    "position": pos
                })
                driver_points[d_id]["total"] += data["weekend_points"]

        if not driver_points:
            return jsonify({"error": f"No driver points available for {year}"}), 404

        # Convert to list and sort by total points
        drivers_list = sorted(driver_points.values(), key=lambda d: d["total"], reverse=True)

        # Assign championship positions
        for idx, driver in enumerate(drivers_list, start=1):
            driver["position"] = idx

        return jsonify(drivers_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver points: {str(e)}"}), 500
