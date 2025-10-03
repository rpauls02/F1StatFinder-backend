from flask import Blueprint, jsonify
from datetime import datetime
from utils import nationality_to_country_code
from cache import get_driver_standings_cached

# Initialize Blueprint for F1 driver standings API
driver_standings_bp = Blueprint("driver_standings", __name__, url_prefix="/api/f1")


@driver_standings_bp.route("/get_driver_standings")
def get_driver_standings():
    """
    Fetch and return driver standings for the current F1 season from Ergast API.
    Results are cached for 1 hour to reduce API calls.
    Returns JSON with driver standings or an error message if the request fails.
    """
    year = datetime.now().year

    try:
        # Fetch driver standings for the current year
        standings_response = get_driver_standings_cached(year)

        # Validate response
        if not standings_response or not getattr(standings_response, "content", None):
            return jsonify({"error": f"No driver standings response found for {year}"}), 404

        standings_df = standings_response.content[0]
        if standings_df.empty:
            return jsonify({"error": f"No driver standings data available for {year}"}), 404

        standings_list = []

        # Process each driver in the standings
        for driver in standings_df.to_dict(orient="records"):
            try:
                first_initial = (
                    driver.get("givenName", "")[0] if driver.get("givenName") else ""
                )
                formatted_name = f"{first_initial}. {driver.get('familyName', '')}".strip()

                standings_list.append({
                    "id": driver.get("driverId", "unknown"),
                    "position": int(driver.get("position", 0)),
                    "nationality": nationality_to_country_code(
                        driver.get("driverNationality", "")
                    ),
                    "name": formatted_name or "Unknown",
                    "constructor": (
                        driver.get("constructorNames")[0]
                        if driver.get("constructorNames")
                        else "Unknown"
                    ),
                    "points": float(driver.get("points", 0) or 0.0),
                })
            except (ValueError, TypeError, IndexError, KeyError):
                # Skip invalid rows without breaking the endpoint
                continue

        if not standings_list:
            return jsonify({"error": f"No valid driver standings found for {year}"}), 404

        # Sort standings by position
        standings_list.sort(key=lambda d: d["position"])

        return jsonify(standings_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver standings: {str(e)}"}), 500
