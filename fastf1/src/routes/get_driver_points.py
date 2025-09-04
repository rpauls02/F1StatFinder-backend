from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
import fastf1
import pandas as pd
from iso3166 import countries

driver_points_bp = Blueprint("driver_points", __name__, url_prefix="/api/f1")


@driver_points_bp.route("/get_driver_points/<int:year>")
def get_driver_points(year):
    try:
        ergast = Ergast(result_type="pandas", auto_cast=True)
        schedule = fastf1.get_event_schedule(year, include_testing=False)

        rounds = schedule["RoundNumber"].tolist()
        races = schedule["EventName"].tolist()
        countries_list = schedule["Country"].tolist()

        # Map each race to ISO country code
        race_country_map = []
        for country_name in countries_list:
            try:
                iso_code = countries.get(country_name).alpha3
            except KeyError:
                iso_code = country_name[:3].upper()  # fallback
            race_country_map.append(iso_code)

        driver_points = {}

        for rnd, race_name, country_code in zip(rounds, races, race_country_map):
            try:
                results = ergast.get_race_results(year, round=rnd).content[0]
            except Exception:
                results = pd.DataFrame()

            try:
                sprint_results = ergast.get_sprint_results(year, round=rnd).content[0]
            except Exception:
                sprint_results = pd.DataFrame()

            # ✅ Merge race + sprint by driver
            combined_results = pd.concat([results, sprint_results], ignore_index=True)

            if not combined_results.empty:
                grouped = (
                    combined_results.groupby("driverId", as_index=False)
                    .agg({
                        "givenName": "first",
                        "familyName": "first",
                        "constructorName": "first",
                        "points": "sum"  # add race + sprint points
                    })
                )
            else:
                grouped = pd.DataFrame()

            for _, r in grouped.iterrows():
                did = r["driverId"]
                name = f"{r.get('givenName','')} {r.get('familyName','')}"
                points = float(r["points"]) if not pd.isna(r["points"]) else 0.0

                if did not in driver_points:
                    driver_points[did] = {
                        "driverId": did,
                        "name": name,
                        "constructor": r.get("constructorName", ""),
                        "total": 0.0,
                        "races": [],
                    }

                driver_points[did]["races"].append(
                    {"name": race_name, "country": country_code, "points": points}
                )
                driver_points[did]["total"] += points

        # Convert dict to list and sort
        drivers_list = list(driver_points.values())
        drivers_list.sort(key=lambda d: d["total"], reverse=True)

        for idx, driver in enumerate(drivers_list, start=1):
            driver["position"] = idx

        return jsonify(drivers_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver points: {str(e)}"}), 500
