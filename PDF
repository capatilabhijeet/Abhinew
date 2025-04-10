import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.title('PDF to Excel Converter')

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        # Parse the text to extract required details
        # For demonstration, let's assume we extracted the following:
        data = {
            'Field': ['PAN', 'Name', 'Mobile Number', 'Email', 'GST', 'Date of Incorporation'],
            'Value': ['ABCDE1234F', 'John Doe', '1234567890', 'john.doe@example.com', '22ABCDE1234F1Z5', '01-01-2000']
        }
        df = pd.DataFrame(data)
        st.write(df)
        
        # Convert DataFrame to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        
        st.download_button(label='Download Excel File',
                           data=processed_data,
                           file_name='extracted_data.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
