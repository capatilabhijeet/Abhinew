header_info = {
    "PAN": personal_info.get("PAN", ""),
    "GST Number": personal_info.get("GSTINNo", personal_info.get("GSTIN", "")),
    "Legal Name of Business": personal_info.get("TradeName1", declaration.get("AssesseeVerName", name_info.get("SurNameOrOrgName", ""))),
    "First Name": name_info.get("FirstName", ""),
    "Middle Name": name_info.get("MiddleName", ""),
    "Last Name": name_info.get("SurNameOrOrgName", ""),
    "Mobile No": itr3.get("PartA_GEN2", {}).get("MobileNo", personal_info.get("MobileNo", "")),
    "Email Address": itr3.get("PartA_GEN2", {}).get("EmailAddress", personal_info.get("EmailAddress", "")),
    "Date of Incorporation": personal_info.get("DOB", ""),
    "Assessment Year": data.get("AssessmentYear", ""),
    "Aadhar Number": personal_info.get("AadhaarCardNo", ""),
    "Assessee Name": itr3.get("Verification", {}).get("Declaration", {}).get("AssesseeVerName", "")
}
