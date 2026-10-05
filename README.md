# Employee Payroll & Salary Analysis System

This project calculates employee payroll details, analyzes salary trends, and saves charts and reports using Python, Pandas, NumPy, and Matplotlib.

## Features
- Employee data management
- Basic salary calculation
- HRA, DA, PF, gross salary, and net salary
- Department-wise salary analysis
- Highest and lowest salary detection
- Salary distribution chart
- Department salary comparison chart
- Payroll export to CSV

## Project Structure

```text
Employee-Payroll-Analysis/
├── data/
│   └── employees.csv
├── output/
│   ├── payroll.csv
│   └── salary_report.txt
├── charts/
│   ├── department_salary.png
│   └── salary_distribution.png
├── main.py
├── payroll.py
├── analysis.py
├── requirements.txt
├── .gitignore
├── README.md
└── venv/
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Project

```bash
python main.py
```

## GitHub Setup

```bash
git init
git add .
git commit -m "Initial employee payroll project"
git branch -M main
git remote add origin <your_github_repository_url>
git push -u origin main
```

## Notes
The code uses a headless Matplotlib backend so charts can be generated without a GUI display.
