from flask import Blueprint, jsonify
from datetime import datetime
from utils import nationality_to_country_code
from cache import get_constructor_standings_cached

constructors_standings_bp = Blueprint(
    "constructor_standings", __name__, url_prefix="/api/f1"
)


@constructors_standings_bp.route("/get_constructor_standings")
def get_constructor_standings():
    """
    Fetch and return constructor standings for the current F1 season from Ergast API.
    Results are cached for 24 hours to reduce API calls.
    Returns JSON with constructor standings or an error message if the request fails.
    """
    year = datetime.now().year

    try:
        # Fetch constructor standings for the current year
        response = get_constructor_standings_cached(year)

        # Check if response is empty or missing content
        if not response or not getattr(response, "content", None) or len(response.content) == 0:
            return jsonify({"error": f"No constructor standings found for {year}"}), 404

        # Extract standings DataFrame from response
        standings_df = response.content[0]

        # Check if DataFrame is empty
        if standings_df.empty:
            return jsonify({"error": f"No constructor standings data available for {year}"}), 404

        # Convert DataFrame to JSON-friendly list
        standings_list = []
        for _, row in standings_df.iterrows():
            try:
                standings_list.append({
                    "id": row.get("constructorId"),
                    "position": int(row.get("position", 0)),
                    "name": row.get("constructorName", "Unknown"),
                    "points": int(row.get("points", 0)),
                    "nationality": nationality_to_country_code(row.get("constructorNationality", "")),
                })
            except (ValueError, TypeError):
                continue  # Skip rows with invalid data

        if not standings_list:
            return jsonify({"error": f"No valid constructor standings for {year}"}), 404

        return jsonify(standings_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor standings: {str(e)}"}), 500
