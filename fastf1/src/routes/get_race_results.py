from flask import Blueprint, jsonify
from cache import get_race_results_cached
import pandas as pd

race_results_bp = Blueprint("race_results", __name__, url_prefix="/api/f1")

@race_results_bp.route("/get_race_results/<int:year>/<int:round>")
def get_race_results(year, round):
    try:
        df = get_race_results_cached(year, round).content[0]

        if df is None or df.empty:
            return jsonify({"error": "No race results available"}), 404

        race_results = []
        for _, row in df.iterrows():
            position = int(row["position"]) if "position" in row and pd.notna(row["position"]) else None
            laps = int(row["laps"]) if "laps" in row and pd.notna(row["laps"]) else None
            points = float(row["points"]) if "points" in row and pd.notna(row["points"]) else None

            race_results.append({
                "position": position,
                "driver": f"{row.get('givenName', '')} {row.get('familyName', '')}".strip(),
                "id": row.get("driverCode", ""),
                "team": row.get("constructorName", ""),
                "laps": laps,
                "time": str(row.get("raceTime")) if "raceTime" in row else None,
                "grid": int(row["grid"]) if "grid" in row and pd.notna(row["grid"]) else None,
                "points": points
            })

        return jsonify({
            "year": year,
            "round": round,
            "results": race_results
        })

    except ValueError:
        return jsonify({"error": "Invalid year or round"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch race results: {str(e)}"}), 500
