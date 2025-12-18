import sqlite3
import pandas as pd

DB_NAME = "gst_reco.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def save_results(df):
    column_map = {
        "Company Name": "company_name",
        "Company GSTIN": "company_gstin",
        "Party GST Name": "party_gst_name",
        "Party GSTIN": "party_gstin",
        "Invoice Number": "invoice_number",
        "Invoice Value": "invoice_value",
        "Taxable Value": "taxable_value",
        "CGST Amount": "cgst",
        "SGST Amount": "sgst",
        "IGST Amount": "igst",
        "Remarks": "remarks"
    }

    df_db = df.rename(columns=column_map)

    conn = get_connection()

    # Silent store (no append issues)
    df_db.to_sql(
        "reconciliation_results",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()






