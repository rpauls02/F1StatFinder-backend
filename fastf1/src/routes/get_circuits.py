from flask import Blueprint, jsonify
from cache import get_circuits_cached
import pandas as pd
import logging
import requests

circuits_bp = Blueprint("circuits", __name__, url_prefix="/api/f1")

@circuits_bp.route("/get_circuits")
def get_circuits():
    """
    Fetch and return a sorted list of F1 circuits from Ergast API.
    Returns JSON with circuit details or an error message if the request fails.
    """
    try:
        # Fetch circuits data with a limit of 100
        circuits_df = get_circuits_cached(limit=100)

        # Check if data is empty
        if circuits_df.empty:
            return jsonify({"error": "No circuit data available"}), 404

        # Convert DataFrame to a list of dictionaries with relevant circuit details
        tracks_list = [
            {
                "id": row.get("circuitId"),
                "name": row.get("circuitName"),
                "location": row.get("locality"),
                "country": row.get("country"),
                "url": row.get("circuitUrl"),
            }
            for _, row in circuits_df.iterrows()
        ]

        # Sort circuits alphabetically by name
        tracks_list.sort(key=lambda track: track["name"])

        # Return JSON response with the sorted circuits
        return jsonify(tracks_list)

    except requests.exceptions.RequestException as e:
        # Catch network-related errors
        return jsonify({"error": "Network error while fetching circuits"}), 503

    except pd.errors.EmptyDataError:
        # Catch empty data from DataFrame
        return jsonify({"error": "Circuit data is empty or malformed"}), 500

    except Exception as e:
        # Catch all other exceptions
        return jsonify({"error": f"Failed to fetch circuits: {str(e)}"}), 500
