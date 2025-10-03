from flask import Blueprint, jsonify
from datetime import datetime
from utils import nationality_to_country_code
from cache import get_driver_standings_cached, get_constructor_standings_cached

# Initialize Blueprint for F1 previous champions API
previous_champions_bp = Blueprint("previous_champions", __name__, url_prefix="/api/f1")


@previous_champions_bp.route("/get_previous_champions")
def get_champions():
    try:
        current_year = datetime.now().year
        results = []

        for year in range(current_year, current_year - 3, -1):
            champion_data = {
                "year": year,
                "wdc": "N/A",
                "wdcNationality": "N/A",
                "wdcPoints": 0.0,
                "wcc": "N/A",
                "wccNationality": "N/A",
                "wccPoints": 0.0,
            }

            try:
                driver_standings = get_driver_standings_cached(year)
                if driver_standings.content and not driver_standings.content[0].empty:
                    wdc_driver = driver_standings.content[0].iloc[0]
                    champion_data["wdc"] = (
                        f"{wdc_driver['givenName'][0]}. {wdc_driver['familyName']}"
                    )
                    wdc_nat = wdc_driver.get("driverNationality")
                    champion_data["wdcNationality"] = (
                        nationality_to_country_code(wdc_nat) or "N/A"
                    )
                    champion_data["wdcPoints"] = float(wdc_driver.get("points", 0) or 0)
            except Exception:
                pass

            try:
                constructor_standings = get_constructor_standings_cached(year)
                if (
                    constructor_standings.content
                    and not constructor_standings.content[0].empty
                ):
                    wcc_constructor = constructor_standings.content[0].iloc[0]
                    champion_data["wcc"] = wcc_constructor["constructorName"]
                    wcc_nat = wcc_constructor.get("constructorNationality")
                    champion_data["wccNationality"] = (
                        nationality_to_country_code(wcc_nat) or "N/A"
                    )
                    champion_data["wccPoints"] = float(
                        wcc_constructor.get("points", 0) or 0
                    )
            except Exception:
                pass

            results.append(champion_data)

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch champions: {str(e)}"}), 500
