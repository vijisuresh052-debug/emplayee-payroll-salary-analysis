import numpy as np
import pandas as pd


def calculate_payroll(df):
    df = df.copy()

    df["HRA"] = np.round(df["Basic_Salary"] * 0.20, 2)
    df["DA"] = np.round(df["Basic_Salary"] * 0.10, 2)
    df["PF"] = np.round(df["Basic_Salary"] * 0.12, 2)

    df["Gross_Salary"] = np.round(
        df["Basic_Salary"] + df["HRA"] + df["DA"],
        2,
    )
    df["Net_Salary"] = np.round(
        df["Gross_Salary"] - df["PF"],
        2,
    )

    return df
