import streamlit as st
import pandas as pd
from io import BytesIO

from gst import preprocess, suvit_style_reconciliation


st.set_page_config(
    page_title="GST Reconciliation Tool",
    layout="wide"
)


st.title("GST Reconciliation Tool")
st.caption("Invoice-wise reconciliation between GST data and Books")


company_name = st.text_input("Company Name")
company_gstin = st.text_input("Company GSTIN")


gst_file = st.file_uploader("Upload GST Data (GSTR-2B / GSTR-1)", type=["xlsx"])
books_file = st.file_uploader("Upload Books Data", type=["xlsx"])


if st.button("Run Reconciliation"):
    if not company_name or not company_gstin:
        st.error("Please enter Company Name and GSTIN")

    elif gst_file and books_file:
        gst_df = preprocess(pd.read_excel(gst_file))
        books_df = preprocess(pd.read_excel(books_file))

        result = suvit_style_reconciliation(
            gst_df,
            books_df,
            company_name,
            company_gstin
        )

        
        st.subheader("Match Status Summary")

        matched_cnt = (result["Status"] == "Matched").sum()
        missing_gst_cnt = (result["Status"] == "Missing in GST").sum()
        missing_books_cnt = (result["Status"] == "Missing in Books").sum()

        s1, s2, s3 = st.columns(3)
        s1.metric("Fully Matched", matched_cnt)
        s2.metric("Missing in GST", missing_gst_cnt)
        s3.metric("Missing in Books", missing_books_cnt)

        
        st.subheader("Match Status – Graph")

        status_df = pd.DataFrame(
            {
                "Count": [
                    matched_cnt,
                    missing_gst_cnt,
                    missing_books_cnt
                ]
            },
            index=[
                "Fully Matched",
                "Missing in GST",
                "Missing in Books"
            ]
        )

        st.bar_chart(status_df)

        
        st.subheader("Amount Difference Summary")

        diff_summary = result["Diff Category"].value_counts().to_frame("Count")
        diff_summary.index.name = "Difference Range"

        st.bar_chart(diff_summary)

        
        st.subheader("Invoice-wise Reconciliation Details")
        st.dataframe(result, use_container_width=True)

        
        output = BytesIO()
        result.to_excel(output, index=False, engine="openpyxl")

        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name="GST_Reconciliation_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("Please upload both GST and Books files")






