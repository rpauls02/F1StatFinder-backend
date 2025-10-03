from flask import Blueprint, jsonify
from cache import get_qualifying_results_cached

qualifying_results_bp = Blueprint("qualifying_results", __name__, url_prefix="/api/f1")

@qualifying_results_bp.route("/get_qualifying_results/<int:year>/<int:round>")
def get_qualifying_results(year, round):
    try:
        response = get_qualifying_results_cached(year, round)

        # Ensure response content exists
        if not response or not response.content or len(response.content) == 0:
            return jsonify({"error": "No qualifying results available"}), 404

        df = response.content[0]

        if df is None or df.empty:
            return jsonify({"error": "No qualifying results available"}), 404

        qualifying_results = []
        for _, row in df.iterrows():
            qualifying_results.append({
                "position": int(row.get('position', 0)),
                "id": row.get("driverCode", ""),
                "driver": f"{row.get('givenName', '')} {row.get('familyName', '')}".strip(),
                "q1_time": str(row.get('Q1')) if row.get('Q1') is not None else None,
                "q2_time": str(row.get('Q2')) if row.get('Q2') is not None else None,
                "q3_time": str(row.get('Q3')) if row.get('Q3') is not None else None,
            })

        return jsonify({
            "year": year,
            "round": round,
            "results": qualifying_results
        })

    except ValueError:
        return jsonify({"error": "Invalid year or round"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch qualifying results: {str(e)}"}), 500
