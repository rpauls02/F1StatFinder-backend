from flask import Blueprint, jsonify
from datetime import datetime, timezone
from cache import (
    get_event_schedule_cached,
    get_race_results_cached,
    get_sprint_results_cached,
    get_qualifying_results_cached,
)

driver_stats_bp = Blueprint("driver_stats", __name__, url_prefix="/api/f1")


@driver_stats_bp.route("/get_driver_stats")
def get_driver_stats():
    """
    Fetch driver statistics (wins, podiums, poles, DNFs) for the current F1 season.
    Returns partial stats for races that have occurred, using cached API calls.
    """
    year = datetime.now().year

    try:
        # Fetch schedule for current year
        schedule = get_event_schedule_cached(year, include_testing=False)
        if schedule.empty:
            return jsonify({"error": f"No event schedule found for {year}"}), 404

        # Only include rounds that have occurred (race date <= now)
        rounds = []
        now = datetime.now(timezone.utc)
        for _, event in schedule.iterrows():
            race_date = event.get("Session5Date")  # Main race session
            if race_date is not None and race_date <= now:
                rounds.append(event["RoundNumber"])

        if not rounds:
            return jsonify({"error": f"No completed races yet for {year}"}), 404

        # Collect all driver IDs that participated in any completed race or sprint
        all_driver_ids = set()
        for rnd in rounds:
            for fn in (get_race_results_cached, get_sprint_results_cached):
                try:
                    res = fn(year, rnd)
                    if res and res.content:
                        df = res.content[0]
                        if not df.empty:
                            all_driver_ids.update(df["driverId"].unique())
                except Exception:
                    continue

        if not all_driver_ids:
            return jsonify({"error": f"No driver data available for {year}"}), 404

        driver_stats_list = []

        # Process each driver
        for driver_id in all_driver_ids:
            wins = podiums = poles = dnfs = 0

            for rnd in rounds:
                # --- Race results ---
                try:
                    race_res = get_race_results_cached(year, rnd)
                    if race_res and race_res.content:
                        df = race_res.content[0]
                        if not df.empty:
                            driver_row = df[df["driverId"] == driver_id]
                            if not driver_row.empty:
                                pos = int(driver_row.iloc[0].get("position", 0))
                                status = str(driver_row.iloc[0].get("status", "")).lower()
                                wins += int(pos == 1)
                                podiums += int(pos <= 3)
                                if not (status.startswith("finished") or "lap" in status):
                                    dnfs += 1
                except Exception:
                    continue

                # --- Sprint results ---
                try:
                    sprint_res = get_sprint_results_cached(year, rnd)
                    if sprint_res and sprint_res.content:
                        df = sprint_res.content[0]
                        if not df.empty:
                            driver_row = df[df["driverId"] == driver_id]
                            if not driver_row.empty:
                                pos = int(driver_row.iloc[0].get("position", 0))
                                status = str(driver_row.iloc[0].get("status", "")).lower()
                                wins += int(pos == 1)
                                podiums += int(pos <= 3)
                                if not (status.startswith("finished") or "lap" in status):
                                    dnfs += 1

                                # Sprint poles based on grid
                                if "grid" in driver_row.columns:
                                    grid = int(driver_row.iloc[0].get("grid", 0))
                                    poles += int(grid == 1)
                except Exception:
                    continue

                # --- Qualifying results (pole positions) ---
                try:
                    quali_res = get_qualifying_results_cached(year, rnd)
                    if quali_res and quali_res.content:
                        df = quali_res.content[0]
                        if not df.empty:
                            driver_row = df[df["driverId"] == driver_id]
                            if not driver_row.empty:
                                pos = int(driver_row.iloc[0].get("position", 0))
                                poles += int(pos == 1)
                except Exception:
                    continue

            driver_stats_list.append({
                "id": driver_id,
                "wins": wins,
                "podiums": podiums,
                "poles": poles,
                "dnfs": dnfs
            })

        return jsonify(driver_stats_list)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch driver stats: {str(e)}"}), 500
