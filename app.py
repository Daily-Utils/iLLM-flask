from flask import Flask, json, request, jsonify
import requests
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
import os
from flask_cors import CORS
from utils import process_csv, process_pdf, json_parse_datetime

app = Flask(__name__)
CORS(app)
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "iLLM flask"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


load_dotenv()
go_server_url = os.getenv("GO_SERVER_URL")
model = os.getenv("MODEL")


@app.route("/send", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename.endswith(".csv"):
        result = process_csv(file, model)
    elif file.filename.endswith(".pdf"):
        result = process_pdf(file, model)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    response = None

    if file.filename.endswith(".csv"):
        response = requests.post(go_server_url + "/context/csv", json=result)
    elif file.filename.endswith(".pdf"):
        response = requests.post(go_server_url + "/context/pdf", json=result)

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        print(response.text + " " + str(response.status_code))
        return jsonify({"error": "Failed to send data to Go server"}), 500

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
