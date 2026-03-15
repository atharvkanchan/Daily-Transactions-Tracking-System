import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

FILE = "transactions.csv"

st.set_page_config(page_title="AI Finance Dashboard", layout="wide")

st.title("💳 AI Personal Finance Dashboard")

# ----------------------------
# Category Detection
# ----------------------------
def detect_category(desc):

    desc = str(desc).lower()

    if "uber" in desc or "ola" in desc:
        return "Travel"

    if "restaurant" in desc or "food" in desc or "pizza" in desc:
        return "Food"

    if "amazon" in desc or "shopping" in desc:
        return "Shopping"

    if "salary" in desc or "income" in desc:
        return "Income"

    if "stock" in desc or "investment" in desc:
        return "Investment"

    if "netflix" in desc:
        return "Entertainment"

    return "Other"


# ----------------------------
# Asset / Liability
# ----------------------------
def detect_type(category):

    if category in ["Income","Investment"]:
        return "Asset"

    return "Liability"


# ----------------------------
# Load Dataset
# ----------------------------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Date","Description","Amount","Category","Type"])


# ----------------------------
# Sidebar
# ----------------------------
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


# ----------------------------
# Upload Bank Statement
# ----------------------------
st.sidebar.header("Upload Bank Statement")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    new_df = pd.read_csv(uploaded_file)

    new_df["Category"] = new_df["Description"].apply(detect_category)

    new_df["Type"] = new_df["Category"].apply(detect_type)

    df = pd.concat([df,new_df],ignore_index=True)

    df.to_csv(FILE,index=False)

    st.success("Bank Statement Imported")


# ----------------------------
# Metrics
# ----------------------------
income = df[df["Type"]=="Asset"]["Amount"].sum()

expense = df[df["Type"]=="Liability"]["Amount"].sum()

networth = income - expense

col1,col2,col3 = st.columns(3)

col1.metric("Income", f"₹{income}")

col2.metric("Expenses", f"₹{expense}")

col3.metric("Net Worth", f"₹{networth}")


# ----------------------------
# Charts
# ----------------------------
st.subheader("Expense Distribution")

category_data = df.groupby("Category")["Amount"].sum().reset_index()

fig = px.pie(category_data, names="Category", values="Amount")

st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# Monthly Trend
# ----------------------------
df["Date"] = pd.to_datetime(df["Date"])

monthly = df.groupby(df["Date"].dt.month)["Amount"].sum()

fig2 = px.line(monthly, title="Monthly Spending Trend")

st.plotly_chart(fig2, use_container_width=True)


# ----------------------------
# ML Prediction
# ----------------------------
st.subheader("AI Spending Prediction")

if len(df) > 5:

    df["Day"] = df["Date"].dt.dayofyear

    X = df[["Day"]]

    y = df["Amount"]

    model = LinearRegression()

    model.fit(X,y)

    future = np.array([[df["Day"].max()+30]])

    prediction = model.predict(future)

    st.metric("Predicted Next Month Spending", f"₹{int(prediction[0])}")


# ----------------------------
# Table
# ----------------------------
st.subheader("Transactions")

st.dataframe(df, use_container_width=True)
