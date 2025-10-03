from flask import Blueprint, jsonify
import pandas as pd
from datetime import datetime, timezone
from cache import (
    get_event_schedule_cached,
    get_race_results_cached,
    get_qualifying_results_cached,
)

constructor_stats_bp = Blueprint("constructor_stats", __name__, url_prefix="/api/f1")


@constructor_stats_bp.route("/get_constructor_stats")
def get_constructor_stats():
    """
    Fetch and return constructor statistics (wins, podiums, poles, DNFs) for the current F1 season.
    Results are cached for 24 hours to reduce API calls.
    Returns JSON with constructor stats or an error message if the request fails.
    """
    year = datetime.now().year
    try:
        # Fetch event schedule for the current year, excluding testing sessions
        schedule = get_event_schedule_cached(year, include_testing=False)

        if schedule.empty:
            return jsonify({"error": f"No event schedule found for {year}"}), 404

        rounds = schedule.get("RoundNumber", []).tolist()
        if not rounds:
            return jsonify({"error": f"No rounds found in schedule for {year}"}), 404

        all_constructor_ids = set()
        # Collect all constructor IDs
        for rnd in rounds:
            try:
                results = get_race_results_cached(year, rnd)
                if results and not results.content[0].empty:
                    all_constructor_ids.update(results.content[0].get("constructorId", []))
            except Exception:
                continue

        if not all_constructor_ids:
            return jsonify({"error": f"No constructor data available for {year}"}), 404

        constructor_stats_list = []

        # Process each constructor
        for constructor_id in all_constructor_ids:
            wins = podiums = poles = dnfs = 0

            for rnd in rounds:
                # Race results
                try:
                    results = get_race_results_cached(year, rnd)
                    if results and not results.content[0].empty:
                        df = results.content[0].copy()
                        df["position"] = pd.to_numeric(df.get("position", pd.Series()), errors="coerce")
                        constructor_rows = df[df.get("constructorId") == constructor_id]
                        if not constructor_rows.empty:
                            wins += int((constructor_rows["position"] == 1).sum())
                            podiums += int((constructor_rows["position"] <= 3).sum())
                            dnfs += int(
                                constructor_rows.get("status", pd.Series()).str.contains(
                                    r"Did Not Finish|Retired|Accident|Collision|Disqualified|Withdrew|"
                                    r"Mechanical|Engine|Gearbox|Transmission|Clutch|Hydraulics|Electrical|"
                                    r"Suspension|Brakes|Differential|Overheating|Oil leak|Wheel|Tyre|"
                                    r"Puncture|Driveshaft|Fuel|Exhaust|Throttle|Steering|Chassis|Battery|"
                                    r"Alternator|Radiator|Turbo|Power Unit|ERS|Spun off|Damage|Debris",
                                    case=False,
                                    na=False,
                                ).sum()
                            )
                except Exception:
                    continue

                # Qualifying results
                try:
                    quali = get_qualifying_results_cached(year, rnd)
                    if quali and not quali.content[0].empty:
                        q_df = quali.content[0].copy()
                        q_df["position"] = pd.to_numeric(q_df.get("position", pd.Series()), errors="coerce")
                        constructor_quali = q_df[q_df.get("constructorId") == constructor_id]
                        if not constructor_quali.empty:
                            poles += int((constructor_quali["position"] == 1).sum())
                except Exception:
                    continue

            constructor_stats_list.append(
                {
                    "id": constructor_id,
                    "wins": wins,
                    "podiums": podiums,
                    "poles": poles,
                    "dnfs": dnfs,
                }
            )

        if not constructor_stats_list:
            return jsonify({"error": f"No constructor stats available for {year}"}), 404

        return jsonify(constructor_stats_list)

    except AttributeError as ae:
        return jsonify({"error": f"Attribute error: {str(ae)}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"Value error: {str(ve)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to fetch constructor stats: {str(e)}"}), 500
