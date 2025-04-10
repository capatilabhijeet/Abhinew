from PyPDF2 import PdfReader
import pandas as pd
from io import BytesIO
import requests

# Download PDF directly from Google Drive (converted link)
pdf_url = "https://drive.google.com/uc?export=download&id=14YSi5d04tAvaHaRfBWCSWdXnH7hPMPsN"
response = requests.get(pdf_url)
pdf_content = BytesIO(response.content)

# Read text from PDF
reader = PdfReader(pdf_content)
all_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_itr_data_from_pdf_text(text):
    data = {
        "PAN": "", "Name": "", "Mobile No": "", "Email": "", "GST Number": "",
        "Date of Incorporation": "",
        "Income from Salaries": 0, "Income from House Property": 0,
        "Profits and gains from Business": 0, "Capital Gains": 0,
        "Income from Other Sources": 0, "Total Exempt Income": 0
    }
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if "PAN" in line and not data["PAN"]: data["PAN"] = line.split()[-1]
        elif "Name" in line and not data["Name"]: data["Name"] = " ".join(line.split()[1:])
        elif "Mobile" in line and not data["Mobile No"]: data["Mobile No"] = line.split()[-1]
        elif "Email" in line and not data["Email"]: data["Email"] = line.split()[-1]
        elif "GST" in line and not data["GST Number"]: data["GST Number"] = line.split()[-1]
        elif "Date of Incorporation" in line: data["Date of Incorporation"] = line.split(":")[-1].strip()
        elif "Income from Salaries" in line: data["Income from Salaries"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
        elif "House Property" in line: data["Income from House Property"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
        elif "Business" in line and "Profits" in line: data["Profits and gains from Business"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
        elif "Capital Gain" in line: data["Capital Gains"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
        elif "Other Sources" in line: data["Income from Other Sources"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
        elif "Total Exempt Income" in line: data["Total Exempt Income"] = float(line.split()[-1].replace(',', '').replace('₹', ''))
    return data

parsed_data = extract_itr_data_from_pdf_text(all_text)
df = pd.DataFrame(parsed_data.items(), columns=["Field", "Value"])
df.to_excel("ITR_Computation_Extracted.xlsx", index=False)
print("✅ Excel file saved: ITR_Computation_Extracted.xlsx")

