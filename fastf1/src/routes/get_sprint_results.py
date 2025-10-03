from flask import Blueprint, jsonify
from cache import get_sprint_results_cached
import pandas as pd

sprint_results_bp = Blueprint("sprint_results", __name__, url_prefix="/api/f1")

@sprint_results_bp.route("/get_sprint_results/<int:year>/<int:round>")
def get_sprint_results(year, round):
    """
    Fetch and return sprint race results for a given F1 season and round.
    Returns JSON with sprint results including driver, team, laps, position, and points.
    """
    try:
        res = get_sprint_results_cached(year, round)
        if not res or not res.content or res.content[0].empty:
            return jsonify({"error": "No sprint results available"}), 404

        df = res.content[0]

        sprint_results = []
        for _, row in df.iterrows():
            sprint_results.append({
                "position": int(row.get("position", 0)),
                "driver": f"{row.get('givenName', '')} {row.get('familyName', '')}".strip(),
                "id": row.get("driverCode", ""),
                "team": row.get("constructorName", ""),
                "laps": int(row["laps"]) if pd.notna(row.get("laps")) else None,
                "time": str(row.get("raceTime", "")),
                "grid": row.get("grid"),
                "points": row.get("points", 0)
            })

        return jsonify({
            "year": year,
            "round": round,
            "results": sprint_results
        })

    except ValueError:
        return jsonify({"error": "Invalid year or round"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sprint results: {str(e)}"}), 500
