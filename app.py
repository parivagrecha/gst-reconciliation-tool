import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from gst import preprocess, reconcile
from database import save_results

st.set_page_config(page_title="GST Reconciliation Tool", layout="wide")

st.title("📊 GST Reconciliation Tool")

# ---------------- COMPANY INPUT ----------------
st.subheader("Company Details")

c1, c2 = st.columns(2)
with c1:
    company_name = st.text_input("Company Name")
with c2:
    company_gstin = st.text_input("Company GSTIN")

st.divider()

# ---------------- FILE UPLOAD ----------------
u1, u2 = st.columns(2)
with u1:
    gst_file = st.file_uploader("Upload GST Excel", type=["xlsx"])
with u2:
    books_file = st.file_uploader("Upload Books Excel", type=["xlsx"])

# ---------------- PROCESS ----------------
if gst_file and books_file and company_name and company_gstin:
    gst_df = preprocess(pd.read_excel(gst_file))
    books_df = preprocess(pd.read_excel(books_file))

    if st.button("🚀 Run Reconciliation"):
        result = reconcile(
            gst_df,
            books_df,
            company_name,
            company_gstin
        )

        # ---------------- SUMMARY ----------------
        st.subheader("📌 Reconciliation Summary")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Invoices", len(result))
        col2.metric(
            "Fully Matched",
            (result["Remarks"] == "Fully Matched").sum()
        )
        col3.metric(
            "Missing in GST",
            (result["Remarks"] == "Missing in GST").sum()
        )
        col4.metric(
            "Missing in Books",
            (result["Remarks"] == "Missing in Books").sum()
        )

        # ---------------- CHART ----------------
        chart_df = result["Remarks"].value_counts().reset_index()
        chart_df.columns = ["Status", "Count"]

        fig = px.bar(
            chart_df,
            x="Status",
            y="Count",
            text="Count",
            title="Invoice Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- STATUS-WISE TABLES ----------------
        st.subheader("✅ Fully Matched Invoices")
        matched_df = result[result["Remarks"] == "Fully Matched"]
        if matched_df.empty:
            st.info("No fully matched invoices")
        else:
            st.dataframe(matched_df, use_container_width=True)

        st.subheader("❌ Missing in GST")
        missing_gst_df = result[result["Remarks"] == "Missing in GST"]
        if missing_gst_df.empty:
            st.info("No invoices missing in GST")
        else:
            st.dataframe(missing_gst_df, use_container_width=True)

        st.subheader("⚠️ Missing in Books")
        missing_books_df = result[result["Remarks"] == "Missing in Books"]
        if missing_books_df.empty:
            st.info("No invoices missing in Books")
        else:
            st.dataframe(missing_books_df, use_container_width=True)

        # ---------------- SAVE ----------------
        save_results(result)

        # ---------------- DOWNLOAD ----------------
        output = BytesIO()
        result.to_excel(output, index=False)

        st.download_button(
            "⬇ Download Full Reconciliation Excel",
            output.getvalue(),
            "gst_reconciliation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Enter company details and upload both files to proceed")




