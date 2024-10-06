import csv
import io
import json
from PyPDF2 import PdfReader

# Function to process CSV files
def process_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)

        # Extract headers and data
        headers = csv_reader.fieldnames
        data = [row for row in csv_reader]

        # Build the JSON object
        result = {
            "body": {
                "headers": headers,
                "data": data
            }
        }
        return result

# Function to process PDF files
def process_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        text_data = []

        # Extract text from all pages
        for page in reader.pages:
            text_data.append(page.extract_text())

        # This part may require customization based on the PDF structure
        headers = ["Content"]
        data = [{"Content": text} for text in text_data]

        # Build the JSON object
        result = {
            "body": {
                "data": data
            }
        }
        return result

# Function to save the result to a file
def save_to_json(output_data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

# Main function
def main():
    file_path = input("Enter the path to your CSV or PDF file: ")
    
    if file_path.endswith('.csv'):
        result = process_csv(file_path)
    elif file_path.endswith('.pdf'):
        result = process_pdf(file_path)
    else:
        print("Unsupported file type. Please provide a CSV or PDF file.")
        return

    output_file = input("Enter the path for the output JSON file: ")
    save_to_json(result, output_file)

    print(f"Processed data saved to {output_file}")

if __name__ == "__main__":
    main()
