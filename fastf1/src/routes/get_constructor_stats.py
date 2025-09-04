from flask import Blueprint, jsonify
import fastf1
from datetime import datetime, timezone
import pandas as pd

constructor_stats_bp = Blueprint("constructor_stats", __name__, url_prefix="/api/f1")


@constructor_stats_bp.route("/get_constructor_stats")
def get_constructor_stats():
    year = datetime.now().year
    now = datetime.now(timezone.utc)

    try:
        ergast = fastf1.ergast.Ergast(result_type="pandas", auto_cast=True)

        # Get the event schedule for the season
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        if schedule.empty:
            return jsonify({"error": f"No event schedule found for {year}"}), 404
        rounds = schedule["RoundNumber"].tolist()

        # Collect all constructor IDs across all races
        all_constructor_ids = set()
        for rnd in rounds:
            try:
                results = ergast.get_race_results(season=year, round=rnd).content[0]
                if not results.empty:
                    all_constructor_ids.update(results["constructorId"].unique())
            except:
                continue  # skip missing or failed rounds

        constructor_stats_list = []

        for constructor_id in all_constructor_ids:
            wins = 0
            podiums = 0
            poles = 0
            name = None
            nationality = None

            for rnd in rounds:
                # Race results
                try:
                    results = ergast.get_race_results(season=year, round=rnd).content[0]
                    if results.empty:
                        continue
                    results["position"] = results["position"].astype(int)
                    constructor_rows = results[results["constructorId"] == constructor_id]

                    if not constructor_rows.empty:
                        wins += int((constructor_rows["position"] == 1).sum())
                        podiums += int((constructor_rows["position"] <= 3).sum())

                        if name is None:
                            first_row = constructor_rows.iloc[0]
                            name = first_row["constructorName"]
                            nationality = first_row["constructorNationality"]
                except:
                    continue

                # Qualifying results → poles
                try:
                    quali = ergast.get_qualifying_results(season=year, round=rnd).content[0]
                    if not quali.empty:
                        quali["position"] = quali["position"].astype(int)
                        constructor_quali = quali[quali["constructorId"] == constructor_id]
                        if not constructor_quali.empty:
                            poles += int((constructor_quali["position"] == 1).sum())
                except:
                    continue

            constructor_stats_list.append({
                "id": constructor_id,
                "name": name,
                "nationality": nationality,
                "wins": wins,
                "podiums": podiums,
                "poles": poles
            })

        # Sort by wins descending, then podiums, then poles
        constructor_stats_list.sort(key=lambda c: (-c["wins"], -c["podiums"], -c["poles"]))

        return jsonify(constructor_stats_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor stats: {str(e)}"}), 500
