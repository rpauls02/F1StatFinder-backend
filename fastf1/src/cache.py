import fastf1
from fastf1.ergast import Ergast
from joblib import Memory
import requests_cache

# ------------------------------------------------------------------
# Setup caching
# ------------------------------------------------------------------

# FastF1 raw data cache (sessions, events, telemetry, laps)
fastf1.Cache.enable_cache("./cache/fastf1")

# Requests cache for Ergast API calls (SQLite, 24h expiry)
requests_cache.install_cache("./cache/ergast", expire_after=86400)

# Ergast instance
ergast = Ergast(result_type="pandas", auto_cast=True)

# Joblib Memory for caching processed function results
memory = Memory("./cache/joblib", verbose=0)


# ------------------------------------------------------------------
# FastF1 wrappers
# ------------------------------------------------------------------
@memory.cache
def get_event_cached(year, gp):
    return fastf1.get_event(year, gp)


@memory.cache
def get_event_schedule_cached(year, include_testing=False):
    return fastf1.get_event_schedule(year, include_testing=include_testing)


@memory.cache
def get_session_cached(year, round, session):
    return fastf1.get_session(year, round, session)


# ------------------------------------------------------------------
# Ergast wrappers (requests-cache handles caching)
# ------------------------------------------------------------------
def get_circuits_cached(limit):
    return ergast.get_circuits(limit=limit)


def get_race_results_cached(season, round_):
    return ergast.get_race_results(season=season, round=round_)


def get_race_schedule_cached(season):
    return ergast.get_race_schedule(season=season)


def get_sprint_results_cached(season, round_):
    return ergast.get_sprint_results(season=season, round=round_)


def get_constructor_standings_cached(season):
    return ergast.get_constructor_standings(season=season)


def get_driver_standings_cached(season):
    return ergast.get_driver_standings(season=season)


def get_seasons_cached(limit):
    return ergast.get_seasons(limit=limit)


def get_qualifying_results_cached(season, round_):
    return ergast.get_qualifying_results(season=season, round=round_)
