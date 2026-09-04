from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "database/database.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_db()
    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


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


@app.route("/bugs")
def bugs():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bugs ORDER BY id DESC")
    bugs = cursor.fetchall()

    connection.close()

    return render_template("bugs.html", bugs=bugs)


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


@app.route("/changes")
def changes():
    return render_template("changes.html")


@app.route("/configuration")
def configuration():
    return render_template("configuration.html")


@app.route("/versions")
def versions():
    return render_template("versions.html")


@app.route("/releases")
def releases():
    return render_template("releases.html")


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)