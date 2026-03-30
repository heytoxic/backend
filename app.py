from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

RESULT_URL = "https://rbse.rankguruji.com/api/result"

FAKE_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept":          "application/json, text/plain, */*",
    "Content-Type":    "application/json",
    "Origin":          "https://rankguruji.com",
    "Referer":         "https://rankguruji.com/",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

@app.route('/api/result', methods=['POST', 'OPTIONS'])
def fetch_result():
    if request.method == 'OPTIONS':
        return _cors_preflight()

    data = request.get_json(force=True) or {}
    roll_no = data.get('roll_no')
    if not roll_no:
        return jsonify({"error": "Roll number missing"}), 400

    board = data.get('board', 'rj')
    year  = data.get('year',  '2026')
    std   = data.get('std',   '10')

    payload = {
        "board":   board,
        "year":    year,
        "std":     std,
        "roll_no": int(roll_no)
    }

    print(f"[Result] std={std} year={year} roll={roll_no}")

    try:
        resp = requests.post(RESULT_URL, json=payload, headers=FAKE_HEADERS, timeout=10)
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"error": f"Upstream error: {resp.status_code}"}), 502
    except requests.Timeout:
        return jsonify({"error": "Timeout — thoda baad try karein"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

def _cors_preflight():
    resp = app.make_response('')
    resp.headers['Access-Control-Allow-Origin']  = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    resp.status_code = 204
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
