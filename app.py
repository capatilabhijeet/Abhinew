import streamlit as st
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="JSON to Excel - ITR Extractor", layout="wide")
st.title("📄 JSON to Excel Converter - ITR Computation Extractor")

uploaded_json = st.file_uploader("Upload your ITR JSON File", type="json")

FIELD_MAP = {
    # Header Info
    "PAN": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "PAN"],
    "First Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "FirstName"],
    "Middle Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "MiddleName"],
    "Last Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "SurNameOrOrgName"],
    "Mobile No": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "Address", "MobileNo"],
    "Email Address": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "Address", "EmailAddress"],
    "Aadhaar Number": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AadhaarCardNo"],
    "Date of Incorporation": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "DOB"],
    "GST Number": ["ITR", "ITR3", "ScheduleGST", "TurnoverGrsRcptForGSTIN", 0, "GSTINNo"],
    "Assessment Year": ["ITR", "ITR3", "Form_ITR3", "AssessmentYear"],
    "Trade Name (Income Tax)": ["ITR", "ITR3", "PartA_GEN2", "NatOfBus", "NatureOfBusiness", 0, "TradeName1"],
    "Business Code": ["ITR", "ITR3", "PartA_GEN2", "NatOfBus", "NatureOfBusiness", 0, "Code"],
    # Salary
    "B1 Salaries": "",
    "Gross Salary": ["ITR", "ITR3", "ScheduleS", "TotalGrossSalary"],
    "Less :Allowances": "",  # Placeholder if available
    "Net Salary": ["ITR", "ITR3", "ScheduleS", "NetSalary"],
    "Less :Deductions u/s 16": ["ITR", "ITR3", "ScheduleS", "DeductionUS16"],
    "Income chargeable under the head \"Salaries\"": ["ITR", "ITR3", "ScheduleS", "TotIncUnderHeadSalaries"],

    # House Property
    "B2 Income from house property": "",
    "Gross rent received/ receivable/ lettable value during the year": "",
    "Less :Tax paid to local authorities": "",
    "Annual Value": "",
    "Less : 30% of Annual Value": "",
    "Less :Interest payable on borrowed capital": "",
    "Less :Arrears/Unrealised rent received during the year less 30%": "",
    "Income chargeable under the head 'House Property'": ["ITR", "ITR3", "ScheduleHP", "IncomeOfHP"],

    # Business
    "B3 Profits and gains from business or profession": "",
    "Profit and gains from business other than speculative business and specified business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainNoSpecBus"],
    "Profit and gains from speculative business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainSpecBus"],
    "Profit and gains from specified business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainSpecifiedBus"],
    "Income chargeable to tax at special rates": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfIncome115BBF"],
    "Income chargeable under the head \"Profits and gains from business or profession\"": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "TotProfBusGain"],

    # Capital Gains
    "B4 Capital gains": "",
    "Short-term chargeable @ 15%": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTerm15Per"],
    "Short-term chargeable @ 30%": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTerm30Per"],
    "Short-term chargeable at applicable rate": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTermAppRate"],
    "Short-term chargeable at special rates in India as per DTAA": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTermSplRateDTAA"],
    "Total short-term": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "TotalShortTerm"],
    "Long-term chargeable @ 10%": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTerm10Per"],
    "Long-term chargeable @ 20%": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTerm20Per"],
    "LTCG chargeable at special rates as per DTAA": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTermSplRateDTAA"],
    "Total Long-term": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "TotalLongTerm"],
    "Income chargeable under the head \"Capital Gain\"": ["ITR", "ITR3", "ScheduleCG", "TotalCapitalGains"],

    # Other Sources
    "B5 Income from other sources": "",
    "Net Income from other sources chargeable to tax at normal applicable rates": ["ITR", "ITR3", "ScheduleOS", "IncomeOtherSource"],
    "Income chargeable to tax at special rate": "",
    "Income from the activity of owning & maintaining race horses": "",
    "Income chargeable under the head \"Income from other sources\"": ["ITR", "ITR3", "ScheduleOS", "IncomeOtherSource"],

    # Audit Info
    "UDIN": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "UDIN"],
    "Audit u/s 44AB applicable": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "LiableSec44ABflg"],
    "Audit u/s 92E applicable": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "LiableSec92Eflg"],
    "Date of furnishing of the audit report": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditReportFurnishDate"],
    "Name of the auditor signing the tax audit report": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditorName"],
    "Membership no. of the auditor": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditorMemNo"],
    "Name of the auditor (proprietorship / firm)": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AudFrmName"],
    "Proprietorship/firm registration number": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AudFrmRegNo"],
    "Permanent Account Number (PAN) of the proprietorship/ firm": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AudFrmPAN"],
    "Date of report of the audit": ["ITR", "ITR3", "PartA_GEN2", "AuditInfo", "AuditDate"],

    # Exempt Income
    "B6 Details of Exempt Income": "",
    "Interest income": "",
    "Net Agricultural income for the year": "",
    "Others exempt income": "",
    "Income not chargeable to tax as per DTAA": "",
    "Pass through income not chargeable to tax": "",
    "Total Exempt Income": ["ITR", "ITR3", "ScheduleEI", "TotExemptInc"]
}

def get_value(data, path):
    if path == "":
        return ""
    try:
        # Generalized handling for any list-indexed field like GSTINNo, Description, TradeName1, Code, etc.
        if isinstance(path, list) and len(path) > 2 and isinstance(path[-2], int):
            container = data
            for p in path[:-2]:
                container = container[p]
            if isinstance(container, list) and len(container) > path[-2]:
                return container[path[-2]].get(path[-1], "")
            return ""
        for p in path:
            data = data[p]
        return data
    except (KeyError, IndexError, TypeError):
        return 0 if isinstance(path, list) and any(x in path[-1] for x in ["Income", "Salary", "Profit"]) else ""

if uploaded_json is not None:
    json_data = json.load(uploaded_json)
    output = {field: get_value(json_data, path) for field, path in FIELD_MAP.items()}

    df = pd.DataFrame(output.items(), columns=["Particulars", "Amount"])
    st.subheader("📊 Computation in Desired Format")
    st.dataframe(df, use_container_width=True)

    # Export to Excel
    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Computation")
    st.download_button(
        label="📥 Download Excel File",
        data=excel_bytes.getvalue(),
        file_name="ITR_Computation_Formatted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
