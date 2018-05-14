from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnection
import re


app = Flask(__name__)
app.secret_key = "ksjdbgoi47ty547"


email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnection("friendsDB")


@app.route("/", methods=["get"])
def reroute():
    return redirect("/users")


@app.route("/users", methods=["get"])
def index():
    # Get users list and send to index template
    users = mysql.query_db("SELECT *, CONCAT_WS(' ', first_name, last_name) full_name, DATE_FORMAT(created_at, '%M %D, %Y') cr_date FROM Users;")

    return render_template("index.html", users = users)


@app.route("/users/<id>", methods=["get"])
def show(id):
    # Get the user and send it to show template
    user_id = int(id)
    sqlQry = f"SELECT *, CONCAT_WS(' ', first_name, last_name) full_name, DATE_FORMAT(created_at, '%M %D, %Y') cr_date FROM Users WHERE id = { user_id };" 
    user = mysql.query_db(sqlQry)

    return render_template("show.html", user = user[0])


@app.route("/users/new", methods=["get"])
def new():
    return render_template("edit.html", callMode = 0)


@app.route("/users/<id>/edit", methods=["get"])
def edit(id):
    # Get the user and send it to show template
    user_id = int(id)
    sqlQry = f"SELECT *, CONCAT_WS(' ', first_name, last_name) full_name, DATE_FORMAT(created_at, '%M %D, %Y') cr_date FROM Users WHERE id = { user_id };" 
    user = mysql.query_db(sqlQry)

    return render_template("edit.html", callMode = 1, user = user[0])


@app.route("/users/<id>/delete", methods=["get"])
def delete(id):
    # Get the user and send it to show template
    user_id = int(id)
    sqlCmd = f"DELETE FROM Users WHERE id = { user_id };" 

    res = mysql.query_db(sqlCmd)

    if res == False:
        flash("Something went wrong!", "error")

    return redirect("/users")


@app.route("/create", methods=["post"])
def create():
    res = checkValidation()
    if res:
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()

        data = { "first_name": first_name,
                 "last_name": last_name,
                 "email": email }
        
        sqlCmd = "INSERT INTO Users (first_name, last_name, email) VALUES (%(first_name)s, %(last_name)s, %(email)s)"

        res = mysql.query_db(sqlCmd, data)

        if res == False:
            flash("Something went wrong!", "error")
            return redirect("/users/new")
        else:
            session.clear()

        return redirect("/users")
    else:
        return redirect("/users/new")


@app.route("/update", methods=["post"])
def update():
    res = checkValidation()
    if res:
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()
        user_id = int(request.form["user_id"])

        data = { "first_name": first_name,
                 "last_name": last_name,
                 "email": email,
                 "user_id": user_id}
        
        sqlCmd = "UPDATE Users SET first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s WHERE id = %(user_id)s"

        res = mysql.query_db(sqlCmd, data)

        if res == False:
            flash("Something went wrong!", "error")
            return redirect(f"/users/{user_id}/edit")
        else:
            session.clear()

        return redirect("/users")
    else:
        return redirect(f"/users/{user_id}/edit")


def checkValidation():
    result = True

    # Validate first_name
    first_name = request.form["first_name"].strip()
    #print(f"[{first_name}]")
    if len(first_name) < 1:
        flash("First name is required!", "first_name")
        result = False
    elif len(first_name) < 2:
        flash("First name should have at least 2 characters!", "first_name")
        result = False
    if not charCheckName(first_name):
        flash("First name accept only alhpabeth and space!", "first_name")
        result = False
        
    # Validate last_name
    last_name = request.form["last_name"].strip()
    #print(f"[{last_name}]")
    if len(last_name) < 1:
        flash("Last name is required!", "last_name")
        result = False
    elif len(last_name) < 2:
        flash("Last name should have at least 2 characters!", "last_name")
        result = False
    if not charCheckName(last_name):
        flash("Last name accept only alhpabeth and space!", "last_name")
        result = False
        
    # Validate email
    email = request.form["email"].strip()
    #print(f"[{email}]")
    if len(email) < 1:
        flash("Email is required!", "email")
        result = False
    elif not email_regex.match(request.form["email"]):
        flash("Email is not valid!", "email")
        result = False

    session["first_name"] = first_name
    session["last_name"] = last_name
    session["email"] = email
    
    return result


def charCheckName(name):
    for c in name:
        if not c.isalpha() and not c.isspace():
            return False

    return True


if __name__ == "__main__":
    app.run(debug = True)
