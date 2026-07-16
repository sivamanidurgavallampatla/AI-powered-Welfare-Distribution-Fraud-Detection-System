# from flask import Flask, render_template, request, redirect, session
# from datetime import datetime
# import pandas as pd
# import joblib
# import json
# import sqlite3

# app = Flask(__name__)
# app.secret_key = "AIPDS_SECRET_2026"

# # ================= DB CONNECTION =================
# def get_db_connection():
#     conn = sqlite3.connect("aipds.db")
#     conn.row_factory = sqlite3.Row
#     return conn

# # ================= LOAD MODEL =================
# model = joblib.load("fraud_model.pkl")

# # ================= LOAD METRICS =================
# with open("metrics.json", "r") as f:
#     metrics = json.load(f)

# # ================= HOME =================
# @app.route('/')
# def home():
#     return render_template("home.html")

# # ================= ABOUT =================
# @app.route('/about')
# def about():
#     return render_template("about.html")

# # ================= LOGIN =================
# @app.route('/login', methods=['GET', 'POST'])
# def login():

#     if request.method == 'POST':

#         email = request.form['email']
#         password = request.form['password']

#         conn = get_db_connection()

#         user = conn.execute(
#             "SELECT * FROM users WHERE email=? AND password=?",
#             (email, password)
#         ).fetchone()

#         conn.close()

#         if user:
#             session['user_id'] = user['id']
#             session['username'] = user['username']
#             return redirect('/dashboard')

#         else:
#             return render_template("login.html", error="Invalid Email or Password")

#     return render_template("login.html")

# # ================= ADMIN =================


# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == "admin" and password == "AIPDS@2026":
#             return redirect('/admin_dashboard')
#         else:
#             return "Invalid Admin Credentials"

#     return render_template("admin_login.html")

# # ================= DASHBOARD =================
# @app.route('/dashboard')
# def dashboard():

#     if 'username' not in session:
#         return redirect('/login')

#     return render_template(
#         "dashboard.html",
#         username=session['username'],
#         accuracy=metrics["accuracy"],
#         precision=metrics["precision"],
#         recall=metrics["recall"],
#         f1_score=metrics["f1_score"],
#         best_model=metrics["best_model"]
#     )

# # ================= UPLOAD =================
# @app.route('/upload')
# def upload():
#     return render_template("upload_data.html")

# # ================= REGISTER =================
# @app.route('/register', methods=['GET', 'POST'])
# def register():

#     if request.method == 'POST':

#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']

#         conn = get_db_connection()

#         user = conn.execute(
#             "SELECT * FROM users WHERE email=?",
#             (email,)
#         ).fetchone()

#         if user:
#             conn.close()
#             return "Email already exists!"

#         conn.execute("""
#             INSERT INTO users(username,email,password)
#             VALUES(?,?,?)
#         """, (username, email, password))

#         conn.commit()
#         conn.close()

#         return redirect('/login')

#     return render_template("register.html")

# # ================= PREDICT =================

# # ================= FRAUD PREDICTION =================
# @app.route('/predict', methods=['POST'])
# def predict():

#     try:

#         # Get uploaded file
#         file = request.files['file']

#         if file.filename == '':
#             return "Please select a CSV file"

#         # Read CSV
#         df = pd.read_csv(file)

#         # PDS column mapping
#         column_mapping = {
#             "Transaction_Step": "step",
#             "Quantity_Distributed": "amount",
#             "Dealer_Stock_Before": "oldbalanceOrg",
#             "Dealer_Stock_After": "newbalanceOrig",
#             "Beneficiary_Stock_Before": "oldbalanceDest",
#             "Beneficiary_Stock_After": "newbalanceDest"
#         }

#         # Validate PDS column names
#         for col in column_mapping.keys():
#             if col not in df.columns:
#                 return f"Missing column: {col}"

#         # Rename to model feature names
#         df.rename(columns=column_mapping, inplace=True)

#         # Model features
#         features = [
#             "step",
#             "amount",
#             "oldbalanceOrg",
#             "newbalanceOrig",
#             "oldbalanceDest",
#             "newbalanceDest"
#         ]

#         # Prepare input
#         X = df[features].copy()
#         X = X.apply(pd.to_numeric, errors='coerce')
#         X = X.fillna(0)

#         # Predict
#         proba = model.predict_proba(X)[:, 1]
#         threshold = 0.05
#         predictions = (proba >= threshold).astype(int)

#         # Add prediction columns
#         df = df.copy()
#         df["Record_No"] = range(1, len(df) + 1)
#         df["Prediction"] = predictions

#         # Keep only fraud records
        
#         # Keep only fraud records
#         fraud_df = df[df["Prediction"] == 1].copy()

#        # ================= AI Detection Reasons =================

#         fraud_types = []
#         reasons = []
#         risk_levels = []

#         for _, row in fraud_df.iterrows():

#             previous = float(row["oldbalanceOrg"])
#             updated = float(row["newbalanceOrig"])
#             quantity = float(row["amount"])
#             beneficiary_before = float(row["oldbalanceDest"])
#             beneficiary_after = float(row["newbalanceDest"])

#             # 1. Dealer Stock Exhaustion
#             if updated == 0 and previous >= 20000:
#                 fraud_type = "Dealer Stock Exhaustion"
#                 reason = "Complete dealer stock exhausted after distribution."
#                 risk = "🔴 High"

#             # 2. Excess Distribution
#             elif quantity >= 100000:
#                 fraud_type = "Excess Distribution"
#                 reason = "Unusually large ration quantity distributed in a single transaction."
#                 risk = "🔴 High"

#             # 3. Inventory Mismatch
#             elif abs((previous - updated) - quantity) > 100:
#                 fraud_type = "Inventory Mismatch"
#                 reason = "Dealer stock change does not match distributed quantity."
#                 risk = "🟠 Medium"

#             # 4. Suspicious Stock Reduction
#             elif updated < previous * 0.10:
#                 fraud_type = "Suspicious Stock Reduction"
#                 reason = "Dealer stock reduced to an unusually low level."
#                 risk = "🟠 Medium"

#             # 5. Beneficiary Quantity Spike
#             elif beneficiary_after > beneficiary_before * 5 and beneficiary_before > 0:
#                 fraud_type = "Beneficiary Quantity Spike"
#                 reason = "Beneficiary received an unusually high quantity."
#                 risk = "🟠 Medium"

#             # 6. Nearly Complete Distribution
#             elif previous > 0 and quantity >= previous * 0.95:
#                 fraud_type = "Nearly Complete Distribution"
#                 reason = "Nearly all available dealer stock was distributed."
#                 risk = "🟡 Low"

#             # 7. AI Anomaly
#             else:
#                 fraud_type = "AI Anomaly"
#                 reason = "AI detected an abnormal PDS transaction pattern."
#                 risk = "🟡 Low"

#             fraud_types.append(fraud_type)
#             reasons.append(reason)
#             risk_levels.append(risk)

#         fraud_df["Fraud_Type"] = fraud_types
#         fraud_df["Reason"] = reasons
#         fraud_df["Risk"] = risk_levels
#         fraud_records = fraud_df.to_dict(orient="records")
#         # Summary
#         total = len(predictions)
#         fraud = int(sum(predictions))
#         safe = total - fraud

#         fraud_percentage = round((fraud / total) * 100, 2) if total > 0 else 0

#         # ================= SAVE HISTORY =================
#         conn = get_db_connection()

#         conn.execute("""
#             INSERT INTO uploads
#             (user_id, filename, upload_date, total_records, fraud_count, safe_count)
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, (
#             session.get("user_id"),
#             file.filename,
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             total,
#             fraud,
#             safe
#         ))

#         conn.commit()
#         conn.close()

#         # ================= SHOW RESULTS =================
#         return render_template(
#             "fraud_results.html",
#             total=total,
#             fraud=fraud,
#             safe=safe,
#             fraud_percentage=fraud_percentage,
#             fraud_records=fraud_records,
#             accuracy=metrics["accuracy"],
#             precision=metrics["precision"],
#             recall=metrics["recall"],
#             f1_score=metrics["f1_score"],
#             best_model=metrics["best_model"]
#         )

#     except Exception as e:
#         return f"Error: {str(e)}"
# # ================= HISTORY =================

# @app.route('/history')
# def history():

#     if 'user_id' not in session:
#         return redirect('/login')

#     conn = get_db_connection()

#     uploads = conn.execute("""
#         SELECT * FROM uploads
#         WHERE user_id = ?
#         ORDER BY upload_date DESC
#     """, (session['user_id'],)).fetchall()

#     conn.close()

#     return render_template("history.html", uploads=uploads)
# # ================= DEBUG =================
# @app.route('/debug_uploads')
# def debug_uploads():
#     conn = get_db_connection()
#     data = conn.execute("SELECT * FROM uploads").fetchall()
#     conn.close()

#     return str([dict(row) for row in data])

# # ================= USERS (DEBUG ONLY) =================
# @app.route('/users')
# def users():

#     conn = get_db_connection()

#     users = conn.execute("SELECT * FROM users").fetchall()

#     conn.close()

#     output = ""
#     for user in users:
#         output += f"""
#         ID: {user['id']}<br>
#         Username: {user['username']}<br>
#         Email: {user['email']}<br>
#         Password: {user['password']}<br><br>
#         """

#     return output
# @app.route('/fraud_records')
# def fraud_records():

#     if 'user_id' not in session:
#         return redirect('/login')

#     conn = get_db_connection()

#     records = conn.execute("""
#         SELECT * FROM predictions
#         ORDER BY id DESC
#     """).fetchall()

#     conn.close()

#     return render_template("fraud_records.html", records=records)
# #================== ADMIN DASHBOARD =============
# @app.route('/admin_dashboard')
# def admin_dashboard():

#     conn = get_db_connection()

#     # USERS COUNT
#     users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

#     # UPLOADS COUNT
#     uploads_count = conn.execute("SELECT COUNT(*) FROM uploads").fetchone()[0]

#     # TOTAL FRAUD
#     fraud_total = conn.execute("SELECT SUM(fraud_count) FROM uploads").fetchone()[0]
#     fraud_total = fraud_total if fraud_total else 0

#     # TOTAL SAFE
#     safe_total = conn.execute("SELECT SUM(safe_count) FROM uploads").fetchone()[0]
#     safe_total = safe_total if safe_total else 0

#     # RECENT USERS
#     users = conn.execute("SELECT * FROM users ORDER BY id DESC LIMIT 5").fetchall()

#     # RECENT UPLOADS
#     uploads = conn.execute("""
#         SELECT uploads.*, users.username
#         FROM uploads
#         JOIN users ON users.id = uploads.user_id
#         ORDER BY uploads.id DESC
#         LIMIT 5
#     """).fetchall()

#     conn.close()

#     return render_template(
#         "admin_dashboard.html",
#         users_count=users_count,
#         uploads_count=uploads_count,
#         fraud_total=fraud_total,
#         safe_total=safe_total,
#         users=users,
#         uploads=uploads
#     )
# # ================ LOGOUT ==================
# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/')
# # ================= REPORTS =================
# @app.route('/reports')
# def reports():
#     return render_template(
#         "reports.html",
#         accuracy=metrics["accuracy"],
#         precision=metrics["precision"],
#         recall=metrics["recall"],
#         f1_score=metrics["f1_score"],
#         best_model=metrics["best_model"],
#         models=metrics["all_models"],
#         fraud_cases=metrics["fraud_cases"],
#         safe_cases=metrics["safe_cases"]
#     )

# # ================= RUN =================
# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import pandas as pd
import joblib
import json
import sqlite3

app = Flask(__name__)
app.secret_key = "AIPDS_SECRET_2026"

# ================= DB =================
def get_db_connection():
    conn = sqlite3.connect("aipds.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= MODEL =================
model = joblib.load("fraud_model.pkl")

# ================= METRICS =================
with open("metrics.json", "r") as f:
    metrics = json.load(f)

# ================= HOME =================
@app.route('/')
def home():
    return render_template("home.html")

# ================= ABOUT =================
@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/dashboard')
def dashboard():
    try:
        if 'username' not in session:
            return redirect('/login')

        return render_template(
            "dashboard.html",
            username=session['username'],
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            best_model=metrics["best_model"]
        )
    except Exception as e:
        return f"Dashboard Debug Error: {str(e)}"

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "AIPDS@2026":
            return redirect('/admin_dashboard')
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")
# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')

        return render_template("login.html", error="Invalid Email or Password")

    return render_template("login.html")
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if user:
            conn.close()
            return "Email already exists!"

        conn.execute("""
            INSERT INTO users(username,email,password)
            VALUES(?,?,?)
        """, (username, email, password))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# ================= FRAUD TYPE (EXPLANATION ONLY) =================
def get_fraud_type(row):
    p = row["Fraud_Probability"]

    # 1. Check for extreme transactional quantities first
    if row["amount"] > 80000:
        return "EXCESSIVE DISTRIBUTION SPIKE"

    # 2. Check for clear computational mismatches (Stock change vs Amount distributed)
    elif abs((row["oldbalanceOrg"] - row["newbalanceOrig"]) - row["amount"]) > 500:
        return "INVENTORY CALCULATION MISMATCH"

    # 3. Check if destination/beneficiary side has anomalous zero-to-hero spikes
    elif row["oldbalanceDest"] == 0 and row["newbalanceDest"] > 50000:
        return "BENEFICIARY STOCK INFLATION"

    # 4. Check for complete stock exhaustion
    elif row["newbalanceOrig"] == 0 and row["oldbalanceOrg"] > 10000:
        return "FULL BALANCE DRAIN"

    # 5. Dynamic fallback: If ML flagged it but no static rules matched
    else:
        return "AI TRANS-PATTERN ANOMALY"

# ================= RISK =================
def get_risk(p):

    if p < 0.20:
        return "🟢 Low"
    elif p < 0.50:
        return "🟠 Medium"
    else:
        return "🔴 High"

# ================= UPLOAD =================
@app.route('/upload')
def upload():
    if 'username' not in session:
        return redirect('/login')

    return render_template("upload_data.html")
# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
def predict():

    try:
        file = request.files['file']

        if file.filename == '':
            return "Please select a CSV file"

        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        # ================= COLUMN MAPPING =================
        mapping = {
            "Transaction_Step": "step",
            "Quantity_Distributed": "amount",
            "Dealer_Stock_Before": "oldbalanceOrg",
            "Dealer_Stock_After": "newbalanceOrig",
            "Beneficiary_Stock_Before": "oldbalanceDest",
            "Beneficiary_Stock_After": "newbalanceDest"
        }

        df.rename(columns=mapping, inplace=True)
        required_columns = [
            "step",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest"
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return f"Missing required columns: {', '.join(missing_columns)}"

        # ================= FEATURE ENGINEERING =================

        
        # Convert transaction type into dummy variables
        
        if "type" not in df.columns:
            df["type"] = "TRANSFER"
        df = pd.get_dummies(df, columns=["type"])

        # Ensure all expected columns exist
        expected_type_cols = [
            "type_CASH_OUT",
            "type_DEBIT",
            "type_PAYMENT",
            "type_TRANSFER"
        ]

        for col in expected_type_cols:
            if col not in df.columns:
                df[col] = 0

        # Engineered Features
        df["orgDiff"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
        df["destDiff"] = df["newbalanceDest"] - df["oldbalanceDest"]

        

        # Final feature order (MUST match training)
        features = [
        'step',
        'amount',
        'oldbalanceOrg',
        'newbalanceOrig',
        'oldbalanceDest',
        'newbalanceDest',
        'orgDiff',
        'destDiff',
        'type_CASH_OUT',
        'type_DEBIT',
        'type_PAYMENT',
        'type_TRANSFER'
    ]

        X = df[features].copy()

        X = X.apply(pd.to_numeric, errors="coerce").fillna(0)
        # ================= ML PREDICTION =================
        proba = model.predict_proba(X)[:, 1]
        threshold = 0.60
        predictions = (proba >= threshold).astype(int)

        df["Fraud_Probability"] = proba
        df["Confidence"] = (proba * 100).round(2)
        df["Prediction"] = predictions

        fraud_records = []
        final_predictions = []

        # ================= HELPERS =================
        def get_fraud_type(row):
            if row["amount"] > 100000:
                return "High Value Transaction"
            elif abs(row["oldbalanceOrg"] - row["newbalanceOrig"]) - row["amount"] > 10000:
                return "Inventory Calculation Mismatch"
            elif row["newbalanceOrig"] < row["oldbalanceOrg"] * 0.2:
                return "Significant Stock Depletion"
            elif row["oldbalanceDest"] != row["newbalanceDest"]:
                return "Beneficiary Stock Anomaly"
            else:
                return "AI-Based Suspicious Pattern"

        def get_risk(prob):
            if prob >= 0.80:
                return "🔴 High"
            elif prob >= 0.50:
                return "🟠 Medium"
            else:
                return "🟢 Low"

        # ================= PROCESS ROWS =================
        for idx, row in df.iterrows():

            ml_flagged = bool(predictions[idx])
            fraud_prob = proba[idx]

            inventory_mismatch = abs(
                (row["oldbalanceOrg"] - row["newbalanceOrig"]) - row["amount"]
            ) > 1000

            is_fraud = ml_flagged or inventory_mismatch

            if is_fraud:

                fraud_type = get_fraud_type(row)
                if inventory_mismatch:
                    risk = "🔴 High"
                elif fraud_prob >= 0.80:
                    risk = "🔴 High"
                elif fraud_prob >= 0.50:
                    risk = "🟠 Medium"
                else:
                    risk = "🟢 Low"

                final_predictions.append(1)

                rec = dict(row)
                rec["Record_No"] = idx + 1
                rec["Detection_Reason"] = fraud_type
                
                rec["Fraud_Probability"] = round(fraud_prob, 4)
                rec["Confidence"] = f"{fraud_prob * 100:.2f}%"
                fraud_records.append(rec)

            else:
                final_predictions.append(0)

        # ================= SUMMARY =================
        total = len(df)
        fraud = sum(final_predictions)
        safe = total - fraud
        fraud_percentage = round((fraud / total) * 100, 2)

        # ================= SAVE TO DB =================
        conn = get_db_connection()

        conn.execute("""
            INSERT INTO uploads
            (user_id, filename, upload_date, total_records, fraud_count, safe_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.get("user_id"),
            file.filename,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total,
            fraud,
            safe
        ))

        conn.commit()
        conn.close()

        # ================= RETURN =================
        return render_template(
            "fraud_results.html",
            total=total,
            fraud=fraud,
            safe=safe,
            fraud_percentage=fraud_percentage,
            fraud_records=fraud_records,
            accuracy=metrics["accuracy"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            best_model=metrics["best_model"]
        )

    except Exception as e:
        print(e)
        return f"Error: {str(e)}"

# ================= HISTORY =================
@app.route('/history')
def history():

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    uploads = conn.execute("""
        SELECT * FROM uploads
        WHERE user_id = ?
        ORDER BY upload_date DESC
    """, (session['user_id'],)).fetchall()
    conn.close()

    return render_template("history.html", uploads=uploads)

# ================= ADMIN =================
@app.route('/admin_dashboard')
def admin_dashboard():

    conn = get_db_connection()

    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    uploads_count = conn.execute("SELECT COUNT(*) FROM uploads").fetchone()[0]

    fraud_total = conn.execute("SELECT SUM(fraud_count) FROM uploads").fetchone()[0] or 0
    safe_total = conn.execute("SELECT SUM(safe_count) FROM uploads").fetchone()[0] or 0

    users = conn.execute("SELECT * FROM users ORDER BY id DESC LIMIT 5").fetchall()

    uploads = conn.execute("""
        SELECT uploads.*, users.username
        FROM uploads
        JOIN users ON users.id = uploads.user_id
        ORDER BY uploads.id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users_count=users_count,
        uploads_count=uploads_count,
        fraud_total=fraud_total,
        safe_total=safe_total,
        users=users,
        uploads=uploads
    )

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
@app.route('/reports')
def reports():
    return render_template(
        "reports.html",
        accuracy=metrics["accuracy"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        f1_score=metrics["f1_score"],
        best_model=metrics["best_model"],
        models=metrics["all_models"],
        fraud_cases=metrics["fraud_cases"],
        safe_cases=metrics["safe_cases"]
    )

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)