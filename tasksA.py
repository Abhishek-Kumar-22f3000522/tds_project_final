import sqlite3
import subprocess
from dateutil.parser import parse
from datetime import datetime
import json
from pathlib import Path
import os
import requests
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
from fastapi import HTTPException
import shutil

load_dotenv()

AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')


def A1(email="22f3000522@ds.study.iitm.ac.in"):
    try:
        process = subprocess.Popen(
            ["uv", "run", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error: {e.stderr}")
# A1()

def A2(prettier_version="prettier@3.4.2", filename="./data/format.md"):
    npx_path = shutil.which("npx")  # Dynamically locate npx
    if not npx_path:
        print("Error: npx not found. Ensure Node.js is installed.")
        return
    
    command = [npx_path, prettier_version, "--write", filename]
    
    try:
        subprocess.run(command, check=True)
        print("Prettier executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")



def A3(filename='/data/dates.txt', targetfile='/data/dates-wednesdays.txt', weekday=2):
    input_file = filename
    output_file = targetfile
    weekday = weekday
    weekday_count = 0

    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date).weekday() == int(weekday)-1)


    with open(output_file, 'w') as file:
        file.write(str(weekday_count))

def A4(filename="/data/contacts.json", targetfile="/data/contacts-sorted.json"):
    # Load the contacts from the JSON file
    with open(filename, 'r') as file:
        contacts = json.load(file)

    # Sort the contacts by last_name and then by first_name
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

    # Write the sorted contacts to the new JSON file
    with open(targetfile, 'w') as file:
        json.dump(sorted_contacts, file, indent=4)

from pathlib import Path

def A5(log_dir_path='/data/logs', output_file_path='/data/logs-recent.txt', num_files=10):
    log_dir = Path(log_dir_path)
    output_file = Path(output_file_path)

    # Get list of .log files sorted by modification time (most recent first)
    log_files = sorted(log_dir.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True)[:num_files]

    # Write the first lines directly to the output file in the correct order
    with output_file.open('w', encoding='utf-8') as f_out:
        for log_file in log_files:
            with log_file.open('r', encoding='utf-8') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(first_line + "\n")



def A6(doc_dir_path='/data/docs', output_file_path='/data/docs/index.json'):
    docs_dir = doc_dir_path
    output_file = output_file_path
    index_data = {}

    # Walk through all files in the docs directory
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                # print(file)
                file_path = os.path.join(root, file)
                # Read the file and find the first occurrence of an H1
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            # Extract the title text after '# '
                            title = line[2:].strip()
                            # Get the relative path without the prefix
                            relative_path = os.path.relpath(file_path, docs_dir).replace('\\', '/')
                            index_data[relative_path] = title
                            break  # Stop after the first H1
    # Write the index data to index.json
    # print(index_data)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)

import re

def A7(filename='/data/email.txt', output_file='/data/email-sender.txt'):
    # Read the email content
    with open(filename, 'r', encoding='utf-8') as file:
        email_content = file.read()

    # Use regex to extract the sender's email
    match = re.search(r"(?i)^From:\s*.*?<?([\w\.-]+@[\w\.-]+\.\w+)>?", email_content, re.MULTILINE)
    sender_email = match.group(1) if match else "Unknown"

    # Write the extracted email to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(sender_email)

import os
import re
import json
import pytesseract
from PIL import Image, ImageEnhance

def A8(**kwargs):
    """
    1. Reads /data/credit_card.png
    2. Extracts a clean 16-digit number via Tesseract OCR
    3. Applies Luhn check. If it fails and the first digit is '9',
       try replacing it with '3' and check again.
    4. Writes the final 16-digit number to /data/credit-card.txt
    """
    input_file = "/data/credit_card.png"
    output_file = "/data/credit-card.txt"

    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

    try:
        # Load and preprocess the image
        img = Image.open(input_file).convert("L")  # Grayscale
        img = ImageEnhance.Contrast(img).enhance(2)  # Increase contrast
        img = ImageEnhance.Sharpness(img).enhance(2)

        # OCR configuration for digit recognition
        custom_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
        extracted_text = pytesseract.image_to_string(img, config=custom_config)

        # Extract multiple 16-digit candidates
        matches = re.findall(r"\b\d{16}\b", extracted_text)
        if not matches:
            return {"error": "OCR failed to extract exactly 16 digits.", "ocr_output": extracted_text}

        # Apply misread fixes
        misread_fixes = {"O": "0", "l": "1", "B": "8", "S": "5", "I": "1"}
        possible_numbers = [fix_misreads(num, misread_fixes) for num in matches]

        # Find the first Luhn-valid number
        final_number = next((num for num in possible_numbers if passes_luhn(num)), None)

        # Try the '9' to '3' fix if needed
        if not final_number and matches[0][0] == "9":
            possible_fix = "3" + matches[0][1:]
            if passes_luhn(possible_fix):
                final_number = possible_fix

        if not final_number:
            return {"error": "Luhn check failed for all candidates.", "recognized_numbers": possible_numbers}

        # Write the valid number to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_number + "\n")

        return {"written_file": output_file, "card_number": final_number}

    except Exception as e:
        return {"error": str(e)}

def fix_misreads(number_str, misread_fixes):
    """Fixes common OCR misread errors."""
    for char, correct in misread_fixes.items():
        number_str = number_str.replace(char, correct)
    return number_str

def passes_luhn(number_str):
    """Returns True if 'number_str' passes the Luhn algorithm."""
    if not number_str.isdigit():
        return False

    digits = [int(d) for d in number_str]
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        digits[i] = doubled - 9 if doubled > 9 else doubled

    return sum(digits) % 10 == 0





import json
import requests
from scipy.spatial.distance import cosine

AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')

def get_embeddings(texts):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": texts
    }
    response = requests.post(
        "http://aiproxy.sanand.workers.dev/openai/v1/embeddings",
        headers=headers,
        data=json.dumps(data)
    )
    response.raise_for_status()
    return [item["embedding"] for item in response.json()["data"]]

def A9(filename='/data/comments.txt', output_filename='/data/comments-similar.txt'):
    # Read comments
    with open(filename, 'r') as f:
        comments = [line.strip() for line in f.readlines() if line.strip()]

    if len(comments) < 2:
        print("Not enough comments to compare.")
        return

    # Get embeddings in batch
    embeddings = get_embeddings(comments)

    # Find the most similar pair
    min_distance = float('inf')
    most_similar = None

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            distance = cosine(embeddings[i], embeddings[j])
            if distance < min_distance:
                min_distance = distance
                most_similar = (comments[i], comments[j])

    # Write the most similar pair to file
    with open(output_filename, 'w') as f:
        f.write(most_similar[0] + '\n')
        f.write(most_similar[1] + '\n')

    print(f"Most similar comments written to {output_filename}")


def A10(filename='/data/ticket-sales.db', output_filename='/data/ticket-sales-gold.txt', query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    # Connect to the SQLite database
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    # Calculate the total sales for the "Gold" ticket type
    cursor.execute(query)
    total_sales = cursor.fetchone()[0]

    # If there are no sales, set total_sales to 0
    total_sales = total_sales if total_sales else 0

    # Write the total sales to the file
    with open(output_filename, 'w') as file:
        file.write(str(total_sales))

    # Close the database connection
    conn.close()
