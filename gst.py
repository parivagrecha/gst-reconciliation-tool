import pandas as pd

def preprocess(df):
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    df["invoice_no"] = (
        df["invoice_no"]
        .astype(str)
        .str.upper()
        .str.replace(r"[^A-Z0-9]", "", regex=True)
    )

    df["gstin"] = df["gstin"].astype(str).str.upper().str.strip()

    if "gst_name" not in df.columns:
        df["gst_name"] = "NA"

    for col in ["invoice_value", "taxable_value", "cgst", "sgst", "igst"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0).astype(float)

    return df


def reconcile(gst_df, books_df, company_name, company_gstin):
    results = []

    for _, g in gst_df.iterrows():
        match = books_df[
            (books_df["gstin"] == g["gstin"]) &
            (books_df["invoice_no"] == g["invoice_no"])
        ]

        remark = "Fully Matched" if not match.empty else "Missing in Books"

        results.append({
            "Company Name": company_name,
            "Company GSTIN": company_gstin,
            "Party GST Name": g["gst_name"],
            "Party GSTIN": g["gstin"],
            "Invoice Number": g["invoice_no"],
            "Invoice Value": g["invoice_value"],
            "Taxable Value": g["taxable_value"],
            "CGST Amount": g["cgst"],
            "SGST Amount": g["sgst"],
            "IGST Amount": g["igst"],
            "Remarks": remark
        })

    for _, b in books_df.iterrows():
        exists = (
            (gst_df["gstin"] == b["gstin"]) &
            (gst_df["invoice_no"] == b["invoice_no"])
        ).any()

        if not exists:
            results.append({
                "Company Name": company_name,
                "Company GSTIN": company_gstin,
                "Party GST Name": b["gst_name"],
                "Party GSTIN": b["gstin"],
                "Invoice Number": b["invoice_no"],
                "Invoice Value": b["invoice_value"],
                "Taxable Value": b["taxable_value"],
                "CGST Amount": b["cgst"],
                "SGST Amount": b["sgst"],
                "IGST Amount": b["igst"],
                "Remarks": "Missing in GST"
            })

    return pd.DataFrame(results)
