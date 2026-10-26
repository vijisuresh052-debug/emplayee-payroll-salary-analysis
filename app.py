from pathlib import Path
import io
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EMPLOYEES_FILE = DATA_DIR / "employees.csv"
USERS_FILE = DATA_DIR / "users.json"

app = Flask(__name__)
app.secret_key = "college-payroll-project-2026"

VALID_USERS = {
    "admin": "admin123",
    "manager": "manager123",
}


def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not EMPLOYEES_FILE.exists():
        sample_data = pd.DataFrame([
            {"Employee_ID": 101, "Name": "Arun", "Department": "IT", "Basic_Salary": 45000},
            {"Employee_ID": 102, "Name": "Bala", "Department": "HR", "Basic_Salary": 38000},
            {"Employee_ID": 103, "Name": "Kavin", "Department": "Finance", "Basic_Salary": 52000},
            {"Employee_ID": 104, "Name": "Ravi", "Department": "IT", "Basic_Salary": 60000},
            {"Employee_ID": 105, "Name": "Deepa", "Department": "Marketing", "Basic_Salary": 42000},
            {"Employee_ID": 106, "Name": "Meena", "Department": "HR", "Basic_Salary": 40000},
            {"Employee_ID": 107, "Name": "Suresh", "Department": "Finance", "Basic_Salary": 55000},
            {"Employee_ID": 108, "Name": "Priya", "Department": "IT", "Basic_Salary": 48000},
            {"Employee_ID": 109, "Name": "Vijay", "Department": "Marketing", "Basic_Salary": 35000},
            {"Employee_ID": 110, "Name": "Anitha", "Department": "Finance", "Basic_Salary": 47000},
        ])
        sample_data.to_csv(EMPLOYEES_FILE, index=False)


def load_registered_users():
    if not USERS_FILE.exists():
        return {}
    with USERS_FILE.open(encoding="utf-8") as users_file:
        return json.load(users_file)


def save_registered_users(users):
    DATA_DIR.mkdir(exist_ok=True)
    with USERS_FILE.open("w", encoding="utf-8") as users_file:
        json.dump(users, users_file, indent=2)


def load_employees():
    ensure_data_file()
    return pd.read_csv(EMPLOYEES_FILE)


def save_employees(df):
    df.to_csv(EMPLOYEES_FILE, index=False)


def calculate_payroll(df):
    df = df.copy()
    df["HRA"] = np.round(df["Basic_Salary"] * 0.20, 2)
    df["DA"] = np.round(df["Basic_Salary"] * 0.10, 2)
    df["PF"] = np.round(df["Basic_Salary"] * 0.12, 2)
    df["Gross_Salary"] = np.round(df["Basic_Salary"] + df["HRA"] + df["DA"], 2)
    df["Net_Salary"] = np.round(df["Gross_Salary"] - df["PF"], 2)
    return df


def get_salary_summary(df):
    summary = {
        "average_salary": round(float(df["Net_Salary"].mean()), 2),
        "highest_salary": round(float(df["Net_Salary"].max()), 2),
        "lowest_salary": round(float(df["Net_Salary"].min()), 2),
        "total_salary": round(float(df["Net_Salary"].sum()), 2),
        "department_average": df.groupby("Department")["Net_Salary"].mean().sort_values(ascending=False),
    }
    return summary


def build_chart_image(kind):
    df = calculate_payroll(load_employees())
    if kind == "bar":
        dept_values = df.groupby("Department")["Net_Salary"].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(dept_values.index, dept_values.values, color="#4f46e5")
        ax.set_title("Department-wise Average Salary")
        ax.set_xlabel("Department")
        ax.set_ylabel("Average Net Salary")
        plt.xticks(rotation=0)
        fig.tight_layout()
    else:
        dept_totals = df.groupby("Department")["Net_Salary"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 7))
        colors = ["#1d4ed8", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#0ea5e9"]
        ax.pie(
            dept_totals.values,
            labels=dept_totals.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors[: len(dept_totals)],
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title("Department Salary Share")
        ax.axis("equal")

    img = io.BytesIO()
    fig.savefig(img, format="png", bbox_inches="tight")
    plt.close(fig)
    img.seek(0)
    return img.getvalue()


@app.before_request
def require_auth():
    allowed_routes = {"login", "signup", "static"}
    if request.endpoint in allowed_routes:
        return None
    if "user" not in session:
        return redirect(url_for("login"))


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        registered_users = load_registered_users()
        is_demo_user = VALID_USERS.get(username) == password
        is_registered_user = username in registered_users and check_password_hash(
            registered_users[username], password
        )
        if is_demo_user or is_registered_user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        registered_users = load_registered_users()

        if not username:
            error = "Enter a username."
        elif username in VALID_USERS or username in registered_users:
            error = "That username is already taken."
        elif len(password) < 8:
            error = "Use a password with at least 8 characters."
        elif password != confirm_password:
            error = "The passwords do not match."
        else:
            registered_users[username] = generate_password_hash(password)
            save_registered_users(registered_users)
            session["user"] = username
            return redirect(url_for("dashboard"))

    return render_template("signup.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    df = load_employees()
    search = request.args.get("search", "").strip().lower()

    if search:
        mask = df.apply(
            lambda row: search in str(row["Name"]).lower()
            or search in str(row["Department"]).lower()
            or search in str(row["Employee_ID"]).lower(),
            axis=1,
        )
        df = df[mask].copy()

    payroll_df = calculate_payroll(df)
    summary = get_salary_summary(payroll_df)
    return render_template(
        "index.html",
        employees=payroll_df.to_dict(orient="records"),
        summary=summary,
        search=search,
        current_user=session.get("user"),
    )


@app.route("/add", methods=["POST"])
def add_employee():
    df = load_employees()
    employee_id = int(request.form["Employee_ID"])
    if df["Employee_ID"].eq(employee_id).any():
        flash("Employee ID already exists! Please enter a different Employee ID.", "error")
        return redirect(url_for("dashboard"))

    new_employee = {
        "Employee_ID": employee_id,
        "Name": request.form["Name"].strip(),
        "Department": request.form["Department"].strip(),
        "Basic_Salary": float(request.form["Basic_Salary"]),
    }
    df = pd.concat([df, pd.DataFrame([new_employee])], ignore_index=True)
    save_employees(df)
    return redirect(url_for("dashboard"))


@app.route("/edit/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    df = load_employees()
    record = df[df["Employee_ID"] == employee_id].iloc[0].to_dict()

    if request.method == "POST":
        df.loc[df["Employee_ID"] == employee_id, "Name"] = request.form["Name"].strip()
        df.loc[df["Employee_ID"] == employee_id, "Department"] = request.form["Department"].strip()
        df.loc[df["Employee_ID"] == employee_id, "Basic_Salary"] = float(request.form["Basic_Salary"])
        save_employees(df)
        return redirect(url_for("dashboard"))

    return render_template("edit_employee.html", employee=record, current_user=session.get("user"))


@app.route("/delete/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    df = load_employees()
    df = df[df["Employee_ID"] != employee_id].copy()
    save_employees(df)
    return redirect(url_for("dashboard"))


@app.route("/report")
def salary_report():
    df = calculate_payroll(load_employees())
    summary = get_salary_summary(df)
    dept_rows = summary["department_average"].reset_index()
    dept_rows.columns = ["Department", "Average_Net_Salary"]
    dept_rows["Average_Net_Salary"] = dept_rows["Average_Net_Salary"].round(2)
    return render_template(
        "report.html",
        summary=summary,
        departments=dept_rows.to_dict(orient="records"),
        current_user=session.get("user"),
        bar_chart_url=url_for("bar_chart"),
        pie_chart_url=url_for("pie_chart"),
    )


@app.route("/export/payroll.csv")
def export_payroll():
    payroll_df = calculate_payroll(load_employees())
    csv_data = payroll_df.to_csv(index=False).encode("utf-8-sig")
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=paywise_payroll.csv"},
    )


@app.route("/bar-chart")
def bar_chart():
    return Response(build_chart_image("bar"), mimetype="image/png")


@app.route("/pie-chart")
def pie_chart():
    return Response(build_chart_image("pie"), mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
