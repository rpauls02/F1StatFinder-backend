from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
import fastf1
import pandas as pd

seasons_bp = Blueprint("seasons", __name__, url_prefix="/api/f1")

@seasons_bp.route("/get_seasons")
def get_seasons():
    try:
        ergast = Ergast(result_type="pandas", auto_cast=True)
        seasons_df = ergast.get_seasons(limit=100)
        seasons_df['season'] = pd.to_numeric(seasons_df['season'], errors='coerce')

        seasons_list = []
        for _, row in seasons_df.iterrows():
            seasons_list.append({
                "year": int(row["season"]),
                "url": row.get("seasonUrl")
            })

        # sort latest season first
        seasons_list.sort(key=lambda s: -s["year"])

        return jsonify(seasons_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch seasons: {str(e)}"}), 500
