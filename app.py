import json
import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="ITR JSON to Excel - Detailed Format", layout="wide")
st.title("🧾 Income Tax JSON to Excel - Detailed Format")

uploaded_file = st.file_uploader("Upload your ITR JSON file", type="json")

# Field mapping template for ITR-3
FIELD_MAP = {
    "PAN": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "PAN"],
    "GST Number": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "GSTINNo"],
    "Legal Name of Business": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "TradeName1"],
    "First Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "FirstName"],
    "Middle Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "MiddleName"],
    "Last Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "SurNameOrOrgName"],
    "Mobile No": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "MobileNo"],
    "Email Address": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "EmailAddress"],
    "Date of Incorporation": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "DOB"],
    "Assessment Year": ["AssessmentYear"],
    "Aadhar Number": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AadhaarCardNo"],
    "Assessee Name": ["ITR", "ITR3", "Verification", "Declaration", "AssesseeVerName"]
}

def get_value_by_path(data, path):
    for key in path:
        data = data.get(key, {}) if isinstance(data, dict) else {}
    return data if isinstance(data, (str, int, float)) else ""

if uploaded_file:
    data = json.load(uploaded_file)

    header_info = {field: get_value_by_path(data, path) for field, path in FIELD_MAP.items()}

    itr3 = data.get("ITR", {}).get("ITR3", {})
    partb_ti = itr3.get("PartB-TI", {})
    filing_status = itr3.get("PartA_GEN1", {}).get("FilingStatus", {})

    filing_info = {
        "Name": get_value_by_path(data, FIELD_MAP["Assessee Name"]),
        "PAN Number": get_value_by_path(data, FIELD_MAP["PAN"]),
        "Filed u/s": filing_status.get("ReturnFiledSection", ""),
        "Acknowledgement No": filing_status.get("AckNum44AB", filing_status.get("AckNo", "")),
        "Date of Filing": filing_status.get("ItrFilingDueDate", filing_status.get("DateOfFiling", "")),
        "Status of CPC": filing_status.get("CpcProcessingStatus", "")
    }

    mapped_fields = {
        "Salaries": "Income chargeable under the head 'Salaries'",
        "IncomeFromHP": "Income chargeable under the head 'House Property'",
        "ProfBusGain.ProfGainNoSpecBus": "Profit and gains from business other than speculative business and specified business",
        "ProfBusGain.TotProfBusGain": "Income chargeable under the head 'Profits and gains from business or profession'",
        "CapGain.ShortTerm.ShortTerm15Per": "Short-term chargeable @ 15%",
        "CapGain.ShortTerm.ShortTerm30Per": "Short-term chargeable @ 30%",
        "CapGain.ShortTerm.ShortTermAppRate": "Short-term chargeable at applicable rate",
        "CapGain.ShortTerm.ShortTermSplRateDTAA": "Short-term chargeable at special rates in India as per DTAA",
        "CapGain.ShortTerm.TotalShortTerm": "Total short-term",
        "CapGain.LongTerm.LongTerm10Per": "Long-term chargeable @ 10%",
        "CapGain.LongTerm.LongTerm20Per": "Long-term chargeable @ 20%",
        "CapGain.LongTerm.LongTermSplRateDTAA": "LTCG chargeable at special rates as per DTAA",
        "CapGain.TotalCapGains": "Income chargeable under the head 'Capital Gain'",
        "IncFromOS.OtherSrcThanOwnRaceHorse": "Net Income from other sources chargeable to tax at normal applicable rates",
        "IncFromOS.TotIncFromOS": "Income chargeable under the head 'Income from other sources'",
        "DeductionsUndSchVIADtl.TotDeductUndSchVIA": "Total Exempt Income"
    }

    def get_nested_value(data, path):
        keys = path.split('.')
        for key in keys:
            data = data.get(key, {}) if isinstance(data, dict) else {}
        return data if isinstance(data, (int, float)) else 0.0

    output_data = {
        "Particulars": [...],  # unchanged for brevity
        "Amount (₹)": []
    }

    for row in output_data["Particulars"]:
        matched_key = None
        for k, v in mapped_fields.items():
            if v == row:
                matched_key = k
                break
        val = get_nested_value(partb_ti, matched_key) if matched_key else 0.0
        output_data["Amount (₹)"].append(val)

    df_computation = pd.DataFrame(output_data)

    st.subheader("🔍 Raw Header Info (Debug)")
    st.json(header_info)

    missing = {k: v for k, v in header_info.items() if not v}
    if missing:
        st.warning(f"⚠️ Missing fields: {', '.join(missing.keys())}")

    header_df = pd.DataFrame(header_info.items(), columns=["Field", "Value"])
    filing_df = pd.DataFrame(filing_info.items(), columns=["Field", "Value"])

    st.success("✅ Computation and header data extracted successfully!")
    st.subheader("Header Information")
    st.dataframe(header_df, use_container_width=True)
    st.dataframe(filing_df, use_container_width=True)

    st.subheader("Income Computation")
    st.dataframe(df_computation, use_container_width=True)

    def to_excel(header_df, filing_df, df_computation):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            header_df.to_excel(writer, index=False, sheet_name='COMPUTATION', startrow=0)
            filing_df.to_excel(writer, index=False, sheet_name='COMPUTATION', startrow=header_df.shape[0] + 3)
            df_computation.to_excel(writer, index=False, sheet_name='COMPUTATION', startrow=header_df.shape[0] + filing_df.shape[0] + 6)
        return output.getvalue()

    excel_data = to_excel(header_df, filing_df, df_computation)

    st.download_button(
        label="📥 Download Computation Excel",
        data=excel_data,
        file_name="computation_total_income.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

