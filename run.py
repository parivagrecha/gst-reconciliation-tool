import pandas as pd
from gst import preprocess, reconcile

gst_df = preprocess(pd.read_excel("gst.xlsx"))
books_df = preprocess(pd.read_excel("books.xlsx"))

result = reconcile(
    gst_df,
    books_df,
    "Demo Company Pvt Ltd",
    "27ABCDE1234F1Z5"
)

print(result)
