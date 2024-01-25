import requests
from bs4 import BeautifulSoup
import re
import json
import csv

# Step 1: Extract OCLC number and store search results
def get_subjects_text(oclc_number):
    if not oclc_number:  # Check if OCLC number is empty
        return "-"  # Return "-" if OCLC number is empty

    url = f"https://search.worldcat.org/title/{oclc_number}"
    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    try:
        # Find the script tag containing "subjectsText" using regex
        pattern = re.compile(r'"subjectsText":\s*\[([\s\S]*?)\]', re.DOTALL)
        match = pattern.search(str(soup))

        # Extract subjectsText if found
        if match:
            subjects_text = match.group(1)
            # Escape unicode characters in the subjects_text
            escaped_subjects_text = json.dumps([subjects_text], ensure_ascii=False)[1:-1]
            # Check if the escaped string is valid JSON
            json.loads(f'[{escaped_subjects_text}]')  # This line validates the JSON string
            return escaped_subjects_text
        else:
            return "-"  # Return "-" if no 'subjectsText' found
    except Exception as e:
        error_message = f"Error extracting 'subjectsText': {e}"
        print(error_message)
        return "-"

# Step 2: Read CSV file - Directly specify the file name instead of the file path
csv_file_name = "worldcat.csv"

with open(csv_file_name, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    rows = list(reader)

    # Step 3: Extract OCLC number and store search results for each row
    for i, row in enumerate(rows):
        if i == 0:  # Skip the header row
            continue

        oclc_number = row[3]  # OCLC number located in the fourth column
        subjects_result = get_subjects_text(oclc_number)

        # Step 4: Store the result in the fifth column
        row.append(subjects_result)

# Step 5: Save the modified content in the fifth column of the existing CSV file
with open(csv_file_name, "a", encoding="utf-8", newline="") as existing_file:
    writer = csv.writer(existing_file)
    writer.writerows(rows)

print("Search and result storage completed.")