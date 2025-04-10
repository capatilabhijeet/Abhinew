import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO

st.set_page_config(page_title="PDF to Excel - ITR Extractor", layout="wide")
st.title("📄 PDF to Excel Converter - ITR Computation Extractor")

uploaded_pdf = st.file_uploader("Upload your ITR Computation PDF", type="pdf")

def safe_parse_number(line):
    try:
        return float(line.split()[-1].replace(',', '').replace('₹', ''))
    except:
        return 0.0

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
        elif "Income from Salaries" in line: data["Income from Salaries"] = safe_parse_number(line)
        elif "House Property" in line: data["Income from House Property"] = safe_parse_number(line)
        elif "Business" in line and "Profits" in line: data["Profits and gains from Business"] = safe_parse_number(line)
        elif "Capital Gain" in line: data["Capital Gains"] = safe_parse_number(line)
        elif "Other Sources" in line: data["Income from Other Sources"] = safe_parse_number(line)
        elif "Total Exempt Income" in line: data["Total Exempt Income"] = safe_parse_number(line)
    return data

if uploaded_pdf is not None:
    try:
        reader = PdfReader(uploaded_pdf)
        all_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        parsed_data = extract_itr_data_from_pdf_text(all_text)

        df = pd.DataFrame(parsed_data.items(), columns=["Field", "Value"])
        st.subheader("📊 Extracted Data")
        st.dataframe(df, use_container_width=True)

        # Create downloadable Excel
        excel_output = BytesIO()
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Computation")
        st.download_button(
            label="📥 Download Excel File",
            data=excel_output.getvalue(),
            file_name="ITR_Computation_Extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Failed to read PDF: {str(e)}")
