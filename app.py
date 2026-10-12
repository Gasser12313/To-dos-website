import os

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def run(sql, params=(), fetch=None):
    """Run one SQL statement. The values always go in `params` (never glued into the SQL)."""
    with pymysql.connect(
        host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor, autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()


def title_errors(title):
    if title.strip() == "":
        return ["Title is required"]
    if len(title) > 200:
        return ["Title is too long (200 characters at most)"]
    return []


def current_filter():
    """Bonus: which list to show. Only these three values are accepted."""
    f = request.args.get("filter", "all")
    return f if f in ("all", "open", "done") else "all"


def back():
    """Redirect to the list and keep the chosen filter."""
    f = current_filter()
    return redirect("/todos" if f == "all" else "/todos?filter=" + f)


def show_todos(add_errors=[], add_title="", edit_id=None, edit_title="", edit_errors=[]):
    rows = run("SELECT todo_id, title, is_done, created_at FROM todos "
               "WHERE user_id = %s ORDER BY todo_id DESC", (session["user_id"],), "all")
    # Bonus: count open to-dos and filter the list (done here, so the SQL stays the same)
    open_count = sum(1 for r in rows if not r["is_done"])
    total = len(rows)
    flt = current_filter()
    if flt == "open":
        rows = [r for r in rows if not r["is_done"]]
    elif flt == "done":
        rows = [r for r in rows if r["is_done"]]
    return render_template("todos.html", todos=rows, add_errors=add_errors, add_title=add_title,
                           edit_id=edit_id, edit_title=edit_title, edit_errors=edit_errors,
                           flt=flt, open_count=open_count, total=total)


@app.route("/")
def index():
    return redirect("/todos" if "user_id" in session else "/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", errors=[], form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []
    if name == "":
        errors.append("Name is required")
    if email == "":
        errors.append("Email is required")
    if password == "":
        errors.append("Password is required")
    if confirm == "":
        errors.append("Confirm password is required")
    if password and confirm and password != confirm:
        errors.append("Passwords do not match")
    if errors:  # show the form again, do not touch the database
        return render_template("register.html", errors=errors, form={"name": name, "email": email})

    # bcrypt only reads the first 72 bytes of a password
    password_hash = bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()
    try:
        run("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
            (email, name, password_hash))
    except pymysql.err.IntegrityError:  # UNIQUE (email) failed: error 1062
        return render_template("register.html", errors=["Email Already Exists"],
                               form={"name": name, "email": email})

    user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), "one")
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", errors=[], form={})

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    errors = []
    if email == "":
        errors.append("Email is required")
    if password == "":
        errors.append("Password is required")
    if errors:
        return render_template("login.html", errors=errors, form={"email": email})

    user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s", (email,), "one")
    # same message whether the e-mail or the password is wrong
    if user is None or not bcrypt.checkpw(password.encode()[:72], user["password_hash"].encode()):
        return render_template("login.html", errors=["Invalid email or password"], form={"email": email})

    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    return redirect("/todos")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/login")
    return show_todos()


@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "")
    errors = title_errors(title)
    if errors:
        return show_todos(add_errors=errors, add_title=title)
    run("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (session["user_id"], title.strip()))
    return back()


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    title = request.form.get("title", "")
    errors = title_errors(title)
    if errors:
        return show_todos(edit_id=todo_id, edit_title=title, edit_errors=errors)
    run("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
        (title.strip(), todo_id, session["user_id"]))
    return back()


@app.route("/todos/<int:todo_id>/done", methods=["POST"])
def done_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    is_done = 1 if request.form.get("is_done") == "1" else 0
    run("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
        (is_done, todo_id, session["user_id"]))
    return back()


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect("/login")
    run("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, session["user_id"]))
    return back()


@app.errorhandler(404)
@app.errorhandler(500)
def error_page(e):  # friendly page instead of a raw error
    return render_template("error.html", message="Something went wrong. Please try again."), e.code


if __name__ == "__main__":
    app.run(port=5000)
