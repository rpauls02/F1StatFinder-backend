from flask import Blueprint, jsonify
from fastf1.ergast import Ergast
import fastf1
import pandas as pd
from iso3166 import countries

constructor_points_bp = Blueprint("constructor_points", __name__, url_prefix="/api/f1")


@constructor_points_bp.route("/get_constructor_points/<int:year>")
def get_constructor_points(year):
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

        constructor_points = {}

        for rnd, race_name, country_code in zip(rounds, races, race_country_map):
            try:
                results = ergast.get_race_results(year, round=rnd).content[0]
            except Exception:
                results = pd.DataFrame()

            try:
                sprint_results = ergast.get_sprint_results(year, round=rnd).content[0]
            except Exception:
                sprint_results = pd.DataFrame()

            # ✅ Merge race + sprint by constructor
            combined_results = pd.concat([results, sprint_results], ignore_index=True)

            if not combined_results.empty:
                grouped = (
                    combined_results.groupby("constructorId", as_index=False)
                    .agg({
                        "constructorName": "first",
                        "points": "sum"  # add all driver + sprint points
                    })
                )
            else:
                grouped = pd.DataFrame()

            for _, r in grouped.iterrows():
                cid = r["constructorId"]
                cname = r.get("constructorName", "Unknown")
                points = float(r["points"]) if not pd.isna(r["points"]) else 0.0

                if cid not in constructor_points:
                    constructor_points[cid] = {
                        "constructorId": cid,
                        "constructor": cname,
                        "total": 0.0,
                        "races": [],
                    }

                constructor_points[cid]["races"].append(
                    {"name": race_name, "country": country_code, "points": points}
                )
                constructor_points[cid]["total"] += points

        # Convert dict to list and sort
        constructors_list = list(constructor_points.values())
        constructors_list.sort(key=lambda c: c["total"], reverse=True)

        for idx, constructor in enumerate(constructors_list, start=1):
            constructor["position"] = idx

        return jsonify(constructors_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor points: {str(e)}"}), 500
