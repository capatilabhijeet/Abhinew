import json
import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="ITR JSON to Excel", layout="centered")
st.title("🧾 Income Tax JSON to Head-wise Excel Converter")

uploaded_file = st.file_uploader("Upload your ITR JSON file", type="json")

if uploaded_file:
    data = json.load(uploaded_file)

    # Navigate to the relevant section
    partb_ti = data.get("ITR", {}).get("ITR3", {}).get("PartB-TI", {})

    # Map fields to the format required
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

    # Helper function to extract nested values
    def get_nested_value(data, path):
        keys = path.split('.')
        for key in keys:
            data = data.get(key, {}) if isinstance(data, dict) else {}
        return data if isinstance(data, (int, float)) else 0.0

    # Create output data
    output_data = []
    for key_path, label in mapped_fields.items():
        value = get_nested_value(partb_ti, key_path)
        output_data.append({"Particulars": label, "Amount (₹)": value})

    df = pd.DataFrame(output_data)

    st.success("✅ Data extracted successfully!")
    st.dataframe(df, use_container_width=True)

    # Convert DataFrame to Excel in-memory
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Headwise Income')
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df)

    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="headwise_income.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
