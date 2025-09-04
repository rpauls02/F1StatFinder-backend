from flask import Blueprint, jsonify
import fastf1
from datetime import datetime, timezone

driver_stats_bp = Blueprint("driver_stats", __name__, url_prefix="/api/f1")


@driver_stats_bp.route("/get_driver_stats")
def get_driver_stats():
    year = datetime.now().year
    now = datetime.now(timezone.utc)

    try:
        ergast = fastf1.ergast.Ergast(result_type="pandas", auto_cast=True)

        # Get the event schedule for the season
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        rounds = schedule["RoundNumber"].tolist()

        # Collect all driver IDs across all races
        all_driver_ids = set()
        for rnd in rounds:
            try:
                results = ergast.get_race_results(season=year, round=rnd).content[0]
                if not results.empty:
                    all_driver_ids.update(results["driverId"].unique())
            except Exception:
                continue  # skip missing or failed rounds

        driver_stats_list = []

        for driver_id in all_driver_ids:
            wins = 0
            podiums = 0
            poles = 0
            dnfs = 0
            name = None
            nationality = None
            constructor = None

            for rnd in rounds:
                # Race results
                try:
                    results = ergast.get_race_results(season=year, round=rnd).content[0]
                    if results.empty:
                        continue
                    results["position"] = results["position"].astype(int, errors="ignore")
                    driver_row = results[results["driverId"] == driver_id]
                    if not driver_row.empty:
                        pos = driver_row.iloc[0]["position"]
                        status = str(driver_row.iloc[0].get("status", "")).lower()

                        wins += int(pos == 1)
                        podiums += int(pos <= 3)

                        # DNF if not "finished" or not ending with "lap(s)"
                        if not (status.startswith("finished") or "lap" in status):
                            dnfs += 1

                        # Capture driver info from first appearance
                        if name is None:
                            name = driver_row.iloc[0].get("familyName", "Unknown")
                            nationality = driver_row.iloc[0].get("driverNationality", "Unknown")
                            constructor = driver_row.iloc[0].get("constructorName", "Unknown")
                except Exception:
                    continue

                # Qualifying results → poles
                try:
                    quali = ergast.get_qualifying_results(season=year, round=rnd).content[0]
                    if not quali.empty:
                        quali["position"] = quali["position"].astype(int)
                        driver_quali = quali[quali["driverId"] == driver_id]
                        if not driver_quali.empty and driver_quali.iloc[0]["position"] == 1:
                            poles += 1
                except Exception:
                    continue

            driver_stats_list.append({
                "id": driver_id,
                "name": name,
                "nationality": nationality,
                "constructor": constructor,
                "wins": wins,
                "podiums": podiums,
                "poles": poles,
                "dnfs": dnfs
            })

        # Sort by wins, then podiums, then poles
        driver_stats_list.sort(key=lambda d: (-d["wins"], -d["podiums"], -d["poles"]))

        return jsonify(driver_stats_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver stats: {str(e)}"}), 500
