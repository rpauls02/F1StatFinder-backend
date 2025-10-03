from flask import Blueprint, jsonify
from datetime import datetime
from utils import nationality_to_country_code, iso2_country
import pandas as pd
from cache import get_race_schedule_cached, get_race_results_cached

recent_rWinners_bp = Blueprint("recent_rWinners", __name__, url_prefix="/api/f1")

@recent_rWinners_bp.route("/get_recent_rWinners")
def get_recent_rWinners():
    """
    Fetch and return winners of the last 5 completed F1 races of the current season.
    Returns JSON with race winner details or an error message if unavailable.
    """
    try:
        year = datetime.now().year

        # Fetch race schedule for the current year
        races = get_race_schedule_cached(year)
        if races is None or races.empty:
            return jsonify({"error": f"No race schedule found for {year}"}), 404

        # Filter for past races (before current UTC time)
        now = datetime.now()
        past_races = races[pd.to_datetime(races["raceDate"]) < now]

        # Get last 5 completed races
        last_5 = past_races.sort_values(by="raceDate", ascending=False).head(5)
        results = []

        for _, race in last_5.iterrows():
            try:
                # Fetch race results for this round
                race_results = get_race_results_cached(year, race["round"])
                if race_results and race_results.content and not race_results.content[0].empty:
                    winner = race_results.content[0].iloc[0]

                    results.append({
                        "year": year,
                        "round": int(race.get("round", 0)),
                        "raceName": race.get("raceName", "N/A"),
                        "circuit": race.get("circuitName", "N/A"),
                        "date": race["raceDate"].strftime("%Y-%m-%d") if pd.notna(race["raceDate"]) else None,
                        "winner": f"{winner.get('givenName','')[0]}. {winner.get('familyName','')}".strip(),
                        "nationality": nationality_to_country_code(winner.get("driverNationality", "N/A")),
                        "constructor": winner.get("constructorName", "N/A"),
                        "country": iso2_country(race.get("country", "N/A")),
                    })
            except Exception:
                continue  # Skip races with invalid results

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Failed to fetch recent race winners: {str(e)}"}), 500
