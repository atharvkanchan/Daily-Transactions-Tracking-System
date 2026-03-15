import numpy as np
from sklearn.linear_model import LinearRegression

def predict_spending(df):

    df["Date"] = pd.to_datetime(df["Date"])

    df["Day"] = df["Date"].dt.dayofyear

    X = df[["Day"]]

    y = df["Amount"]

    model = LinearRegression()

    model.fit(X,y)

    future = np.array([[df["Day"].max()+30]])

    prediction = model.predict(future)

    return prediction[0]
