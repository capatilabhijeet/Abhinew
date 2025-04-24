import streamlit as st
import pandas as pd
import json
from io import BytesIO

# JSON Field Mapping
FIELD_MAP = {
    # Header Info
    "PAN": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "PAN"],
    "GST Number": ["ITR", "ITR3", "ScheduleGST", "TurnoverGrsRcptForGSTIN", 0, "GSTINNo"],
    "Legal Name of Business": ["ITR", "ITR3", "PartA_GEN2", "NatOfBus", "NatureOfBusiness", 0, "TradeName1"],
    "Mobile No": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "MobileNo"],
    "Email Address": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "EmailAddress"],
    "Assessment Year": ["ITR", "ITR3", "Form_ITR3", "AssessmentYear"],
    "Assessee Name": ["ITR", "ITR3", "PartA_GEN1", "PersonalInfo", "AssesseeName", "SurNameOrOrgName"],

    # Income Heads
    "Gross Salary": ["ITR", "ITR3", "ScheduleS", "TotalGrossSalary"],
    "Net Salary": ["ITR", "ITR3", "ScheduleS", "NetSalary"],
    "Deductions u/s 16": ["ITR", "ITR3", "ScheduleS", "DeductionUS16"],
    "Income chargeable under the head 'Salaries'": ["ITR", "ITR3", "ScheduleS", "TotIncUnderHeadSalaries"],

    "Gross rent received": ["ITR", "ITR3", "PartB-TI", "IncomeFromHP"],
    "Income chargeable under the head 'House Property'": ["ITR", "ITR3", "PartB-TI", "IncomeFromHP"],

    "Profit and gains from business other than speculative business and specified business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainNoSpecBus"],
    "Profit and gains from speculative business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainSpecBus"],
    "Profit and gains from specified business": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfGainSpecifiedBus"],
    "Income chargeable to tax at special rates": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "ProfIncome115BBF"],
    "Income chargeable under the head 'Profits and gains from business or profession'": ["ITR", "ITR3", "PartB-TI", "ProfBusGain", "TotProfBusGain"],

    "Short-term chargeable @ 15%": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTerm15Per"],
    "Short-term chargeable @ 30%": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTerm30Per"],
    "Short-term chargeable at applicable rate": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTermAppRate"],
    "Short-term chargeable at special rates in India as per DTAA": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "ShortTermSplRateDTAA"],
    "Total short-term": ["ITR", "ITR3", "PartB-TI", "CapGain", "ShortTerm", "TotalShortTerm"],
    "Long-term chargeable @ 10%": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTerm10Per"],
    "Long-term chargeable @ 20%": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTerm20Per"],
    "LTCG chargeable at special rates as per DTAA": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "LongTermSplRateDTAA"],
    "Total Long-term": ["ITR", "ITR3", "PartB-TI", "CapGain", "LongTerm", "TotalLongTerm"],
    "Income chargeable under the head 'Capital Gain'": ["ITR", "ITR3", "PartB-TI", "CapGain", "TotalCapGains"],

    "Net Income from other sources chargeable to tax at normal applicable rates": ["ITR", "ITR3", "PartB-TI", "IncFromOS", "OtherSrcThanOwnRaceHorse"],
    "Income chargeable to tax at special rate": ["ITR", "ITR3", "PartB-TI", "IncFromOS", "IncChargblSplRate"],
    "Income from the activity of owning & maintaining race horses": ["ITR", "ITR3", "PartB-TI", "IncFromOS", "FromOwnRaceHorse"],
    "Income chargeable under the head 'Income from other sources'": ["ITR", "ITR3", "PartB-TI", "IncFromOS", "TotIncFromOS"],

    "Total Exempt Income": ["ITR", "ITR3", "ScheduleEI", "TotExemptInc"]
}

def get_value(data, path):
    if path == "":
        return ""
    try:
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
        return 0

st.title("📂 JSON to Excel Converter - Income Tax Computation")
uploaded_json = st.file_uploader("Upload JSON File", type="json")

if uploaded_json is not None:
    json_data = json.load(uploaded_json)
    output = {field: get_value(json_data, path) for field, path in FIELD_MAP.items()}

    df = pd.DataFrame(output.items(), columns=["Particulars", "Amount"])
    st.subheader("📊 Computation in Desired Format")
    st.dataframe(df, use_container_width=True)

    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Computation")

    st.download_button(
        label="📥 Download Excel File",
        data=excel_bytes.getvalue(),
        file_name="ITR_Computation_Formatted.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
