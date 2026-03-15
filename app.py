import streamlit as st
import pandas as pd
import plotly.express as px
from utils.categorizer import detect_category, detect_type
from utils.parser import parse_bank_statement
from utils.ml_predictor import predict_spending
import os

FILE = "transactions.csv"

st.set_page_config(page_title="AI Finance Dashboard", layout="wide")

st.title("💳 AI Personal Finance Dashboard")

# Dark mode
dark = st.sidebar.toggle("🌙 Dark Mode")

if dark:
    st.markdown("""
    <style>
    body {background-color:#0f172a;color:white}
    </style>
    """, unsafe_allow_html=True)

# Load data
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date","Description","Amount","Category","Type"])

# Sidebar input
st.sidebar.header("Add Transaction")

desc = st.sidebar.text_input("Description")

amount = st.sidebar.number_input("Amount")

date = st.sidebar.date_input("Date")

if st.sidebar.button("Add"):

    cat = detect_category(desc)

    typ = detect_type(cat)

    new = {
        "Date":date,
        "Description":desc,
        "Amount":amount,
        "Category":cat,
        "Type":typ
    }

    df = pd.concat([df,pd.DataFrame([new])],ignore_index=True)

    df.to_csv(FILE,index=False)

# Upload bank statement
st.sidebar.header("Upload Bank Statement")

file = st.sidebar.file_uploader("Upload CSV")

if file:

    new_df = parse_bank_statement(file)

    new_df["Category"] = new_df["Description"].apply(detect_category)

    new_df["Type"] = new_df["Category"].apply(detect_type)

    df = pd.concat([df,new_df],ignore_index=True)

    df.to_csv(FILE,index=False)

# Metrics
income = df[df["Type"]=="Asset"]["Amount"].sum()

expense = df[df["Type"]=="Liability"]["Amount"].sum()

networth = income - expense

col1,col2,col3 = st.columns(3)

col1.metric("Income",f"₹{income}")

col2.metric("Expenses",f"₹{expense}")

col3.metric("Net Worth",f"₹{networth}")

# Charts
st.subheader("Expense Distribution")

cat = df.groupby("Category")["Amount"].sum().reset_index()

fig = px.pie(cat,names="Category",values="Amount")

st.plotly_chart(fig,use_container_width=True)

# Monthly trend
df["Date"] = pd.to_datetime(df["Date"])

monthly = df.groupby(df["Date"].dt.month)["Amount"].sum()

fig2 = px.line(monthly,title="Monthly Spending Trend")

st.plotly_chart(fig2,use_container_width=True)

# AI insights
st.subheader("AI Insights")

top_cat = cat.sort_values("Amount",ascending=False).iloc[0]["Category"]

st.info(f"Highest spending category: {top_cat}")

# ML prediction
pred = predict_spending(df)

st.metric("Predicted next month spending",f"₹{int(pred)}")

# Table
st.subheader("Transactions")

st.dataframe(df,use_container_width=True)
