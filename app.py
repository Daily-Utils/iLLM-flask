from flask import Flask, request, jsonify
import csv
import io
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
go_server_url = os.getenv("GO_SERVER_URL")


def process_csv(file):
    file_content = file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(file_content))

    headers = csv_reader.fieldnames
    data = [row for row in csv_reader]

    return {"body": str({"headers": headers, "data": data})}


def process_pdf(file):
    reader = PdfReader(file)
    text_data = []

    for page in reader.pages:
        text_data.append(page.extract_text())

    data = [{"Content": text} for text in text_data]

    return {"body": {"data": str(data)}}


@app.route("/csv_response", methods=["POST"])
def csv_response():
    data = request.json
    print("Received CSV data: " + str(data))
    return jsonify({"message": data}), 200


@app.route("/pdf_response", methods=["POST"])
def pdf_response():
    data = request.json
    print("Received PDF data: " + str(data))
    return jsonify({"message": data}), 200


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

    print("result: " + str(result))

    response = None

    if file.filename.endswith(".csv"):
        response = requests.post(go_server_url + "/csv", result)
    elif file.filename.endswith(".pdf"):
        response = requests.post(go_server_url + "/pdf", result)

    if response.status_code == 200:
        return jsonify({"message": "Data successfully sent to Go server"}), 200
    else:
        return jsonify({"error": "Failed to send data to Go server"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
