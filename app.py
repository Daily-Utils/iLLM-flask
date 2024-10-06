from flask import Flask, request, jsonify
import csv
import io
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
go_server_url = os.getenv('GO_SERVER_URL')  # Fetch the URL from the environment variable

# Function to process CSV files
def process_csv(file):
    file_content = file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(file_content))

    # Extract headers and data
    headers = csv_reader.fieldnames
    data = [row for row in csv_reader]

    # Build the JSON object
    return {
        "body": {
            "headers": headers,
            "data": data
        }
    }

# Function to process PDF files
def process_pdf(file):
    reader = PdfReader(file)
    text_data = []

    # Extract text from all pages
    for page in reader.pages:
        text_data.append(page.extract_text())

    # Build the JSON object
    # headers = ["Content"]
    data = [{"Content": text} for text in text_data]

    return {
        "body": {
            "data": data
        }
    }

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename.endswith('.csv'):
        result = process_csv(file)
    elif file.filename.endswith('.pdf'):
        result = process_pdf(file)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Send the JSON data to the Go server
    response = requests.post(go_server_url, json=result)

    if response.status_code == 200:
        return jsonify({"message": "Data successfully sent to Go server"}), 200
    else:
        return jsonify({"error": "Failed to send data to Go server"}), 500

if __name__ == '__main__':
    app.run(debug=True)
