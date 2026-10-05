from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
CHARTS_DIR = ROOT / "charts"


def salary_analysis(df):
    OUTPUT_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)

    average_salary = df["Net_Salary"].mean()
    highest_employee = df.loc[df["Net_Salary"].idxmax()]
    lowest_employee = df.loc[df["Net_Salary"].idxmin()]
    department_salary = df.groupby("Department")["Net_Salary"].mean().sort_values(ascending=False)

    print("\n===== SALARY ANALYSIS =====")
    print(f"\nAverage Net Salary: {average_salary:.2f}")
    print(f"\nHighest Paid Employee: {highest_employee['Name']} - {highest_employee['Net_Salary']:.2f}")
    print(f"\nLowest Paid Employee: {lowest_employee['Name']} - {lowest_employee['Net_Salary']:.2f}")
    print("\nDepartment-wise Average Salary:")
    print(department_salary)

    report_lines = [
        "EMPLOYEE PAYROLL & SALARY ANALYSIS REPORT",
        "========================================",
        f"Average Net Salary: {average_salary:.2f}",
        f"Highest Paid Employee: {highest_employee['Name']} - {highest_employee['Net_Salary']:.2f}",
        f"Lowest Paid Employee: {lowest_employee['Name']} - {lowest_employee['Net_Salary']:.2f}",
        "",
        "Department-wise Average Salary:",
    ]

    for dept, value in department_salary.items():
        report_lines.append(f"{dept}: {value:.2f}")

    report_path = OUTPUT_DIR / "salary_report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    plt.figure(figsize=(8, 5))
    department_salary.plot(kind="bar", color="steelblue")
    plt.title("Department-wise Average Salary")
    plt.xlabel("Department")
    plt.ylabel("Average Net Salary")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "department_salary.png")
    plt.close()


def salary_distribution(df):
    CHARTS_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.hist(df["Net_Salary"], bins=5, color="darkorange", edgecolor="black")
    plt.title("Employee Salary Distribution")
    plt.xlabel("Net Salary")
    plt.ylabel("Number of Employees")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "salary_distribution.png")
    plt.close()
