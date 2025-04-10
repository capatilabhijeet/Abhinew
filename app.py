import json
import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="ITR JSON to Excel - Detailed Format", layout="wide")
st.title("🧾 Income Tax JSON to Excel - Detailed Format")

uploaded_file = st.file_uploader("Upload your ITR JSON file", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    itr3 = data.get("ITR", {}).get("ITR3", {})
    partb_ti = itr3.get("PartB-TI", {})
    personal_info = itr3.get("PartA_GEN1", {}).get("PersonalInfo", {})
    filing_status = itr3.get("PartA_GEN1", {}).get("FilingStatus", {})
    name_info = personal_info.get("AssesseeName", {})

    # Extract header data
    header_info = {
        "PAN": personal_info.get("PAN", ""),
        "GST Number": personal_info.get("GSTIN", ""),
        "Legal Name of Business": name_info.get("FirstName", ""),
        "First Name": name_info.get("FirstName", ""),
        "Middle Name": name_info.get("MiddleName", ""),
        "Last Name": name_info.get("SurNameOrOrgName", ""),
        "Mobile No": personal_info.get("MobileNo", ""),
        "Email Address": personal_info.get("EmailAddress", ""),
        "DOB": personal_info.get("DateOfFormation", ""),
        "Assessment Year": data.get("Form_ITR3", {}).get("AssessmentYear", "")
    }

    filing_info = {
        "Name": name_info.get("FirstName", ""),
        "PAN Number": personal_info.get("PAN", ""),
        "Filed u/s": filing_status.get("ReturnFiledSection", ""),
        "Acknowledgement No": filing_status.get("AckNo", ""),
        "Date of Filing": filing_status.get("DateOfFiling", ""),
        "Status of CPC": filing_status.get("CpcProcessingStatus", "")
    }

    # Prepare income mappings
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
        "Particulars": [
            "B1 - Salaries", "Gross Salary", "Less :Allowances", "Net Salary", "Less :Deductions u/s 16",
            "Income chargeable under the head 'Salaries'",
            "B2 - Income from House Property", "Gross rent received/ receivable/ lettable value during the year",
            "Less :Tax paid to local authorities", "Annual Value", "Less : 30% of Annual Value",
            "Less :Interest payable on borrowed capital", "Less :Arrears/Unrealised rent received during the year less 30%",
            "Income chargeable under the head 'House Property'",
            "B3 - Profits and gains from business or profession",
            "Profit and gains from business other than speculative business and specified business",
            "Profit and gains from speculative business", "Profit and gains from specified business",
            "Income chargeable to tax at special rates",
            "Income chargeable under the head 'Profits and gains from business or profession'",
            "B4 - Capital gains", "Short term", "Short-term chargeable @ 15%", "Short-term chargeable @ 30%",
            "Short-term chargeable at applicable rate", "Short-term chargeable at special rates in India as per DTAA",
            "Total short-term", "Long term", "Long-term chargeable @ 10%", "Long-term chargeable @ 20%",
            "LTCG chargeable at special rates as per DTAA", "Total Long-term",
            "Income chargeable under the head 'Capital Gain'",
            "B5 - Income from other sources", "Net Income from other sources chargeable to tax at normal applicable rates",
            "Income chargeable to tax at special rate", "Income from the activity of owning & maintaining race horses",
            "Income chargeable under the head 'Income from other sources'",
            "B6 - Details of Exempt Income", "Interest income", "Net Agricultural income for the year",
            "Others exempt income", "Income not chargeable to tax as per DTAA",
            "Pass through income not chargeable to tax", "Total Exempt Income"
        ],
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
