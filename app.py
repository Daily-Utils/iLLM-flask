from flask import Flask, request, jsonify
import csv
import io
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint
import os

app = Flask(__name__)
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "iLLM flask"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


load_dotenv()
go_server_url = os.getenv("GO_SERVER_URL")
model = os.getenv("MODEL")


def process_csv(file):
    file_content = file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(file_content))

    headers = csv_reader.fieldnames
    data = [row for row in csv_reader]

    return {"model": model, "body": str({"headers": headers, "data": data})}


def process_pdf(file):
    reader = PdfReader(file)
    text_data = []

    for page in reader.pages:
        text_data.append(page.extract_text())

    data = [{"Content": text} for text in text_data]

    return {"model": model, "body": {"data": str(data)}}


@app.route("/send", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename.endswith(".csv"):
        result = process_csv(file)
    elif file.filename.endswith(".pdf"):
        result = process_pdf(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    response = None

    if file.filename.endswith(".csv"):
        response = requests.post(go_server_url + "/context/csv", json=result)
    elif file.filename.endswith(".pdf"):
        response = requests.post(go_server_url + "/context/pdf", json=result)

    if response.status_code == 200:
        return jsonify({"message": "Data successfully sent to Go server"}), 200
    else:
        print(response.text + " " + str(response.status_code))
        return jsonify({"error": "Failed to send data to Go server"}), 500

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
