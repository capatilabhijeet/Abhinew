    import streamlit as st
import pandas as pd
import json
from io import BytesIO

# JSON Field Mapping
FIELD_MAP = {
    "Provisions": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "Provisions", "TotProvisions"],
    "Sundry Creditors": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "CurrLiabilities", "SundryCred"],
    "Fixed Assets": ["ITR", "ITR3", "PARTA_BS", "FundApply", "FixedAsset", "TotFixedAsset"],
    "Investments": ["ITR", "ITR3", "PARTA_BS", "FundApply", "Investments", "TotInvestments"],
    "Loans and Advances": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrAssetLoanAdv", "LoanAdv", "TotLoanAdv"],
    "Other Current Assets": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrAssetLoanAdv", "CurrAsset", "OthCurrAsset"],
    "Cash and Bank Balances": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrAssetLoanAdv", "CurrAsset", "CashOrBankBal", "TotCashOrBankBal"],
    "Sundry Debtors": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrAssetLoanAdv", "CurrAsset", "SndryDebtors"],
    "Inventories": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrAssetLoanAdv", "CurrAsset", "Inventories", "TotInventries"],
    "Total Current Liabilities": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "CurrLiabilities", "TotCurrLiabilities"],
    "Interest accrued but not due on loans": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "CurrLiabilities", "AccrIntNotDue"],
    "Interest Accrued on leased Assets": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "CurrLiabilities", "AccrIntonLeasedAsset"],
    "Liability for leased Assets": ["ITR", "ITR3", "PARTA_BS", "FundApply", "CurrLiabilitiesProv", "CurrLiabilities", "LiabForLeasedAsset"],
    "Advances": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "Advances", "TotalAdvances"],
    "Deferred Tax Liability": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "DeferredTax"],
    "Total Loan Funds": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "LoanFunds", "TotLoanFund"],
    "Unsecured Loans": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "LoanFunds", "UnsecrLoan", "TotUnSecrLoan"],
    "Secured Loans": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "LoanFunds", "SecrLoan", "TotSecrLoan"],
    "Total Proprietor Funds": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "PropFund", "TotPropFund"],
    "Capital": ["ITR", "ITR3", "PARTA_BS", "FundSrc", "PropFund", "PropCap"],

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
