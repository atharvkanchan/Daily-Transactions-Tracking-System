import pandas as pd

def parse_bank_statement(file):

    df = pd.read_csv(file)

    if "Debit" in df.columns and "Credit" in df.columns:

        df["Amount"] = df["Credit"].fillna(0) - df["Debit"].fillna(0)

    df.rename(columns={"Narration":"Description"}, inplace=True)

    return df[["Date","Description","Amount"]]
