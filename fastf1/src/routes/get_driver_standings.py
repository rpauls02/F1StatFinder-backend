from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
from datetime import datetime
from utils import nationality_to_country_code

driver_standings_bp = Blueprint("driver_standings", __name__, url_prefix="/api/f1")


@driver_standings_bp.route("/get_driver_standings")
def get_driver_standings():
    year = datetime.now().year
    try:
        ergast = Ergast(result_type="pandas", auto_cast=True)
        standings_response = ergast.get_driver_standings(year)

        if not standings_response.content or standings_response.content[0].empty:
            return jsonify({"error": f"No driver standings found for {year}"}), 404

        standings_list = []

        for driver in standings_response.content[0].to_dict(orient="records"):
            first_initial = (
                driver.get("givenName", "")[0] if driver.get("givenName") else ""
            )
            formatted_name = f"{first_initial}. {driver.get('familyName', '')}"

            standings_list.append(
                {
                    "id": driver.get("driverId"),
                    "position": int(driver.get("position", 0)),
                    "nationality": nationality_to_country_code(
                        driver.get("driverNationality", "")
                    ),
                    "name": formatted_name,
                    "constructor": driver.get("constructorNames", ["Unknown"])[0],
                    "points": int(driver.get("points", 0)),
                }
            )

        # Sort by position just in case
        standings_list.sort(key=lambda d: d["position"])

        return jsonify(standings_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver standings: {str(e)}"}), 500
