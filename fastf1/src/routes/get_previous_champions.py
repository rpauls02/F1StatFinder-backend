from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
from datetime import datetime

champions_bp = Blueprint("champions", __name__, url_prefix="/api/f1")


@champions_bp.route("/get_champions")
def get_champions():
    current_year = datetime.now().year
    results = []

    try:
        ergast = Ergast(result_type="pandas", auto_cast=True)

        # Get the last 5 seasons including the current year
        for year in range(current_year, current_year - 5, -1):
            # Default values
            wdc_name = "N/A"
            wcc_name = "N/A"

            # Fetch driver standings
            try:
                driver_standings = ergast.get_driver_standings(year)
                if driver_standings.content and not driver_standings.content[0].empty:
                    wdc_driver = driver_standings.content[0].iloc[0]
                    wdc_name = f"{wdc_driver['givenName'][0]}. {wdc_driver['familyName']}"
            except Exception:
                pass  # Keep "N/A" if fetching fails

            # Fetch constructor standings
            try:
                constructor_standings = ergast.get_constructor_standings(year)
                if constructor_standings.content and not constructor_standings.content[0].empty:
                    wcc_constructor = constructor_standings.content[0].iloc[0]
                    wcc_name = wcc_constructor["constructorName"]
            except Exception:
                pass  # Keep "N/A" if fetching fails

            results.append({
                "year": year,
                "wdc": wdc_name,
                "wcc": wcc_name
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch champions: {str(e)}"}), 500
