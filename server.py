from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json

    pressure = data.get("pressure")
    temperature = data.get("temperature")

    timestamp = datetime.datetime.now().isoformat()

    print(f"[{timestamp}] {pressure} Pa | {temperature} C")

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
