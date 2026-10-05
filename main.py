import pandas as pd

from payroll import calculate_payroll
from analysis import salary_analysis, salary_distribution


def main():
    print("====================================")
    print(" EMPLOYEE PAYROLL & SALARY ANALYSIS")
    print("====================================")

    df = pd.read_csv("data/employees.csv")
    print("\nEmployee Data:")
    print(df)

    df = calculate_payroll(df)
    print("\n===== PAYROLL DETAILS =====")
    print(df)

    df.to_csv("output/payroll.csv", index=False)
    print("\nPayroll saved to output/payroll.csv")

    salary_analysis(df)
    salary_distribution(df)

    print("\nPayroll generated successfully!")


if __name__ == "__main__":
    main()
