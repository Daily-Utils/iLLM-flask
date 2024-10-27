import csv
import io

def process_csv(file, model: str):
    file_content = file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(file_content))

    headers = csv_reader.fieldnames
    data = [row for row in csv_reader]

    return {"model": model, "body": str({"headers": headers, "data": data})}
