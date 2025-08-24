from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import date

app = Flask(__name__)

# Database connection
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rakshita2305",
        database="billing_system"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Filters
    customer_filter = request.args.get("customer")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = "SELECT invoices.*, customers.name AS customer_name FROM invoices JOIN customers ON invoices.customer_id = customers.customer_id WHERE 1=1"
    params = []

    if customer_filter:
        query += " AND invoices.customer_id = %s"
        params.append(customer_filter)
    if start_date and end_date:
        query += " AND invoice_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    cursor.execute(query, params)
    invoices = cursor.fetchall()

    # KPI calculations
    cursor.execute("SELECT SUM(amount) AS total_invoiced FROM invoices")
    total_invoiced = cursor.fetchone()["total_invoiced"] or 0

    cursor.execute("SELECT SUM(amount) AS total_received FROM payments")
    total_received = cursor.fetchone()["total_received"] or 0

    total_outstanding = total_invoiced - total_received

    cursor.execute("SELECT SUM(amount) AS overdue FROM invoices WHERE due_date < %s", (date.today(),))
    overdue = cursor.fetchone()["overdue"] or 0
    percent_overdue = round((overdue / total_invoiced) * 100, 2) if total_invoiced else 0

    # Chart Data: Top 5 Customers by Outstanding
    cursor.execute("""
        SELECT c.name, SUM(i.amount) - IFNULL(SUM(p.amount), 0) AS outstanding
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        LEFT JOIN payments p ON i.invoice_id = p.invoice_id
        GROUP BY c.customer_id
        ORDER BY outstanding DESC
        LIMIT 5
    """)
    chart_data = cursor.fetchall()
    chart_labels = [row["name"] for row in chart_data]
    chart_values = [float(row["outstanding"]) for row in chart_data]

    # Customer list for filter dropdown
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    db.close()

    return render_template(
        "index.html",
        invoices=invoices,
        total_invoiced=total_invoiced,
        total_received=total_received,
        total_outstanding=total_outstanding,
        percent_overdue=percent_overdue,
        chart_labels=chart_labels,
        chart_values=chart_values,
        customers=customers
    )

@app.route("/record_payment", methods=["POST"])
def record_payment():
    invoice_id = request.form["invoice_id"]
    amount = request.form["amount"]
    payment_date = request.form["payment_date"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO payments (invoice_id, amount, payment_date) VALUES (%s, %s, %s)",
                   (invoice_id, amount, payment_date))
    db.commit()
    db.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
