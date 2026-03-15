import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import pdfplumber

FILE = "transactions.csv"

# Load dataset
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date","Description","Amount","Category","Type"])

# -------------------------
# Category Detection
# -------------------------
def detect_category(desc):

    desc = str(desc).lower()

    if "uber" in desc or "ola" in desc or "bus" in desc:
        return "Travel"

    if "restaurant" in desc or "food" in desc or "pizza" in desc:
        return "Food"

    if "amazon" in desc or "shopping" in desc:
        return "Shopping"

    if "salary" in desc or "income" in desc:
        return "Income"

    if "stock" in desc or "investment" in desc:
        return "Investment"

    return "Other"

# -------------------------
# Asset / Liability
# -------------------------
def detect_type(category):

    if category in ["Income","Investment"]:
        return "Asset"

    return "Liability"

# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

st.title("💰 Smart Expense Tracker")

# -------------------------
# Sidebar Transaction Input
# -------------------------
st.sidebar.header("Add Transaction")

desc = st.sidebar.text_input("Description")

amount = st.sidebar.number_input("Amount", min_value=0.0)

date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Add Transaction"):

    category = detect_category(desc)
    t_type = detect_type(category)

    new_data = {
        "Date": date,
        "Description": desc,
        "Amount": amount,
        "Category": category,
        "Type": t_type
    }

    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    df.to_csv(FILE, index=False)

    st.sidebar.success("Transaction Added")

# -------------------------
# Upload Bank Statement
# -------------------------
st.sidebar.header("Upload Bank Statement")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV / Excel / PDF",
    type=["csv","xlsx","pdf"]
)

def process_csv(file):
    data = pd.read_csv(file)
    return data

def process_excel(file):
    data = pd.read_excel(file)
    return data

def process_pdf(file):

    rows = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if table:
                for row in table:
                    rows.append(row)

    df_pdf = pd.DataFrame(rows)

    return df_pdf

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        new_df = process_csv(uploaded_file)

    elif uploaded_file.name.endswith(".xlsx"):
        new_df = process_excel(uploaded_file)

    elif uploaded_file.name.endswith(".pdf"):
        new_df = process_pdf(uploaded_file)

    new_df["Category"] = new_df["Description"].apply(detect_category)
    new_df["Type"] = new_df["Category"].apply(detect_type)

    df = pd.concat([df,new_df],ignore_index=True)
    df.to_csv(FILE,index=False)

    st.success("Bank Statement Imported")

# -------------------------
# Financial Summary
# -------------------------
assets = df[df["Type"]=="Asset"]["Amount"].sum()
liabilities = df[df["Type"]=="Liability"]["Amount"].sum()
networth = assets - liabilities

col1,col2,col3 = st.columns(3)

col1.metric("Total Assets", f"₹{assets}")
col2.metric("Total Liabilities", f"₹{liabilities}")
col3.metric("Net Worth", f"₹{networth}")

# -------------------------
# Charts
# -------------------------
st.subheader("Expense Categories")

if len(df) > 0:

    category_data = df.groupby("Category")["Amount"].sum().reset_index()

    fig = px.pie(
        category_data,
        values="Amount",
        names="Category",
        title="Expense Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Transactions Table
# -------------------------
st.subheader("Transaction History")

st.dataframe(df, use_container_width=True)
