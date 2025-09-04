from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
from datetime import datetime
from utils import nationality_to_country_code

constructors_standings_bp = Blueprint("constructor_standings", __name__, url_prefix="/api/f1")


@constructors_standings_bp.route("/get_constructor_standings")
def get_constructor_standings():
    year = datetime.now().year
    try:
        ergast = Ergast(result_type="pandas", auto_cast=True)
        response = ergast.get_constructor_standings(year)

        # Check if response is empty or missing content
        if not response or not response.content or len(response.content) == 0:
            return jsonify({"error": f"No constructor standings found for {year}"}), 404

        standings_df = response.content[0]
        if standings_df.empty:
            return jsonify({"error": f"No constructor standings data available for {year}"}), 404

        # Convert to JSON-friendly list
        standings_list = [
            {
                "id": row["constructorId"],
                "position": int(row["position"]),
                "name": row["constructorName"],
                "points": int(row["points"]),
                "nationality": nationality_to_country_code(row["constructorNationality"])
            }
            for _, row in standings_df.iterrows()
        ]

        return jsonify(standings_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor standings: {str(e)}"}), 500
