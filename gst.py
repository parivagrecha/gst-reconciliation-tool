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

    if "taxable_value" not in df.columns:
        df["taxable_value"] = 0.0

    df["taxable_value"] = df["taxable_value"].fillna(0).astype(float)

    return df


def diff_category(diff):
    if diff <= 30:
        return "Ignored (₹1–30)"
    elif diff <= 1000:
        return "Low Diff (₹31–1000)"
    elif diff <= 5000:
        return "High Diff (₹1001–5000)"
    else:
        return "Critical Diff (>₹5000)"


def suvit_style_reconciliation(gst_df, books_df, company_name, company_gstin):
    results = []
    matched_books = set()

    for _, g in gst_df.iterrows():
        match = books_df[
            (books_df["gstin"] == g["gstin"]) &
            (books_df["invoice_no"] == g["invoice_no"])
        ]

        if not match.empty:
            b = match.iloc[0]
            matched_books.add(b.name)
            status = "Matched"
            diff = abs(g["taxable_value"] - b["taxable_value"])
            books_amt = b["taxable_value"]
            books_inv = b["invoice_no"]
        else:
            status = "Missing in Books"
            diff = g["taxable_value"]
            books_amt = 0
            books_inv = None

        results.append({
            "Company Name": company_name,
            "Company GSTIN": company_gstin,
            "Party GSTIN": g["gstin"],
            "GST Invoice": g["invoice_no"],
            "Books Invoice": books_inv,
            "GST Amount": g["taxable_value"],
            "Books Amount": books_amt,
            "Amount Difference": diff,
            "Status": status
        })

    for _, b in books_df.iterrows():
        if b.name not in matched_books:
            results.append({
                "Company Name": company_name,
                "Company GSTIN": company_gstin,
                "Party GSTIN": b["gstin"],
                "GST Invoice": None,
                "Books Invoice": b["invoice_no"],
                "GST Amount": 0,
                "Books Amount": b["taxable_value"],
                "Amount Difference": b["taxable_value"],
                "Status": "Missing in GST"
            })

    df = pd.DataFrame(results)
    df["Diff Category"] = df["Amount Difference"].apply(diff_category)

    return df
