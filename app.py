import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="JSON to Excel - ITR Extractor", layout="wide")
st.title("📄 JSON to Excel Converter - ITR Computation Extractor")

uploaded_json = st.file_uploader("Upload your ITR JSON File", type="json")

FIELD_MAP = {
    "PAN": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "PAN"],
    "First Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "FirstName"],
    "Middle Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "MiddleName"],
    "Last Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "SurNameOrOrgName"],
    "Mobile No": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "Address", "MobileNo"],
    "Email Address": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "Address", "EmailAddress"],
    "Aadhaar Number": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AadhaarCardNo"],
    "Date of Incorporation": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "DOB"],
    "GST Number": ["ITR", "ITR3", "PartA_GEN2", "NatOfBus", "NatureOfBusiness", 0, "TradeName1"],
    "Assessment Year": ["ITR", "ITR3", "Form_ITR3", "AssessmentYear"],

    "Net Salary": ["ITR", "ITR3", "ScheduleS", "NetSalary"],
    "Income from House Property": ["ITR", "ITR3", "ScheduleHP", "IncomeOfHP"],
    "Profits and gains from Business": ["ITR", "ITR3", "ITR3ScheduleBP", "NetPLAftAdjBusOthThanSpec"],
    "Income from Capital Gains": ["ITR", "ITR3", "ScheduleCG", "TotalCapitalGains"],
    "Income from Other Sources": ["ITR", "ITR3", "ScheduleOS", "IncomeOtherSource"],
    "Total Exempt Income": ["ITR", "ITR3", "ScheduleEI", "TotExemptInc"],

    "Auditor Name": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditorName"],
    "Auditor Membership No": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditorMemNo"],
    "Auditor Firm": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AudFrmName"],
    "Date of Audit Report": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditDate"],
    "Acknowledgement No": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AckNum44AB"],
    "Date of Filing": ["ITR", "ITR3", "PartA_GEN1", "FilingStatus", "ItrFilingDueDate"]
}

def get_value(data, path):
    try:
        for p in path:
            data = data[p]
        return data
    except (KeyError, IndexError, TypeError):
        return ""

if uploaded_json is not None:
    json_data = json.load(uploaded_json)
    output = {field: get_value(json_data, path) for field, path in FIELD_MAP.items()}

    df = pd.DataFrame(output.items(), columns=["Field", "Value"])
    st.subheader("📊 Extracted Data")
    st.dataframe(df, use_container_width=True)

    # Export to Excel
    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Computation")
    st.download_button(
        label="📥 Download Excel File",
        data=excel_bytes.getvalue(),
        file_name="ITR_Computation_Extracted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
