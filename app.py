from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Database location
DATABASE = os.path.join("database", "database.db")

# Create database folder automatically
os.makedirs("database", exist_ok=True)


# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# -------------------------------------------------
# CREATE TABLES
# -------------------------------------------------

def create_tables():

    connection = get_db()
    cursor = connection.cursor()

    # Bug table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            assigned_to TEXT NOT NULL
        )
    """)

    # Change Request table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS change_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            reason TEXT NOT NULL,
            priority TEXT NOT NULL,
            requested_by TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@app.route("/login")
def login():
    return render_template("login.html")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
def dashboard():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM bugs")
    total_bugs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bugs WHERE status='Open'")
    open_bugs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bugs WHERE status='In Progress'")
    progress_bugs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bugs WHERE status='Closed'")
    closed_bugs = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        progress_bugs=progress_bugs,
        closed_bugs=closed_bugs
    )


# -------------------------------------------------
# BUGS
# -------------------------------------------------

@app.route("/bugs")
def bugs():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bugs ORDER BY id DESC")
    bugs = cursor.fetchall()

    connection.close()

    return render_template("bugs.html", bugs=bugs)


# -------------------------------------------------
# ADD BUG
# -------------------------------------------------

@app.route("/add_bug", methods=["GET", "POST"])
def add_bug():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]
        severity = request.form["severity"]
        assigned_to = request.form["assigned_to"]

        connection = get_db()

        connection.execute("""
            INSERT INTO bugs
            (title, description, priority, severity, status, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            description,
            priority,
            severity,
            "Open",
            assigned_to
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("bugs"))

    return render_template("add_bug.html")


# -------------------------------------------------
# UPDATE BUG
# -------------------------------------------------

@app.route("/update_bug/<int:bug_id>", methods=["POST"])
def update_bug(bug_id):

    status = request.form["status"]

    connection = get_db()

    connection.execute(
        "UPDATE bugs SET status=? WHERE id=?",
        (status, bug_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("bugs"))


# =================================================
# CHANGE REQUEST MODULE
# =================================================

# -------------------------------------------------
# VIEW CHANGE REQUESTS
# -------------------------------------------------

@app.route("/changes")
def changes():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM change_requests
        ORDER BY id DESC
    """)

    change_requests = cursor.fetchall()

    connection.close()

    return render_template(
        "changes.html",
        change_requests=change_requests
    )


# -------------------------------------------------
# CREATE CHANGE REQUEST
# -------------------------------------------------

@app.route("/create_change", methods=["GET", "POST"])
def create_change():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        reason = request.form["reason"]
        priority = request.form["priority"]
        requested_by = request.form["requested_by"]

        connection = get_db()

        connection.execute("""
            INSERT INTO change_requests
            (
                title,
                description,
                reason,
                priority,
                requested_by,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            title,
            description,
            reason,
            priority,
            requested_by,
            "Under Review"
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("changes"))

    return render_template("changes.html", change_requests=[])


# -------------------------------------------------
# UPDATE CHANGE REQUEST STATUS
# -------------------------------------------------

@app.route("/update_change/<int:change_id>", methods=["POST"])
def update_change(change_id):

    status = request.form["status"]

    connection = get_db()

    connection.execute("""
        UPDATE change_requests
        SET status=?
        WHERE id=?
    """, (status, change_id))

    connection.commit()
    connection.close()

    return redirect(url_for("changes"))


# -------------------------------------------------
# OTHER MODULES
# -------------------------------------------------

@app.route("/configuration")
def configuration():
    return render_template("configuration.html")


@app.route("/versions")
def versions():
    return render_template("versions.html")


@app.route("/releases")
def releases():
    return render_template("releases.html")


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    create_tables()

    app.run(debug=True)