from flask import Blueprint, jsonify
import pandas as pd
from cache import get_seasons_cached

seasons_bp = Blueprint("seasons", __name__, url_prefix="/api/f1")

@seasons_bp.route("/get_seasons")
def get_seasons():
    """
    Fetch and return a list of F1 seasons from the Ergast API.
    Seasons are sorted in descending order (latest first).
    Returns JSON with season years and URLs or an error message if the request fails.
    """
    try:
        # Fetch seasons data with a limit of 100
        seasons_df = get_seasons_cached(limit=100)
        if seasons_df is None or seasons_df.empty:
            return jsonify({"error": "No seasons data found"}), 404

        # Convert season column to numeric safely
        seasons_df["season"] = pd.to_numeric(seasons_df.get("season", pd.Series()), errors="coerce")

        # Build list of valid seasons
        seasons_list = [
            {"year": int(row["season"]), "url": row.get("seasonUrl", "")}
            for _, row in seasons_df.iterrows()
            if pd.notna(row["season"])
        ]

        # Sort seasons descending (latest first)
        seasons_list.sort(key=lambda s: -s["year"])

        return jsonify(seasons_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch seasons: {str(e)}"}), 500
