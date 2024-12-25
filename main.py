from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import hashlib
import re # for detecting tags

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Configuration
db_config = {
    'host': 'localhost',  # Change this to your MySQL host
    'user': 'final_backend',  # Change this to your MySQL username
    'password': 'passwd',  # Change this to your MySQL password
    'database': 'DB_final'  # Change this to your MySQL database name
}

# Database Connection

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Login Page

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone() # fetchone() returns None if no record is found

        if result and result[0] == hashed_password:
            session['username'] = username
            return redirect("/welcome")
        
        else:
            flash("Invalid username or password.", "danger")

        
        # Close the connection
        cursor.close()
        conn.close()

        
    return render_template("login.html")

# Welcome Page

@app.route("/welcome")
def welcome():
    if 'username' not in session:
        return redirect("/")
    return render_template("welcome.html")

# Logout

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect("/")

#Edit password

@app.route("/change_passwd", methods=["GET","POST"])
def profile():
    if 'username' not in session:
        return redirect("/")
    if request.method == "POST":
        username = session['username']
        oldpasswd = request.form['oldpassword']
        n1 = request.form['n1password']
        n2 = request.form['n2password']

        oldpasswd = hashlib.sha256(oldpasswd.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone() # fetchone() returns None if no record is found

        if result and result[0] == oldpasswd:
            if n1 == n2:
                n1 = hashlib.sha256(n1.encode()).hexdigest()
                cursor.execute("UPDATE users SET password = %s WHERE username = %s", (n1, username, ))
                conn.commit()
                return redirect("welcome")
            else:
                flash("Invalid old password or new password is not identical.", "danger")
        
        else:
            flash("Invalid old password or new password is not identical.", "danger")
        
        cursor.close()
        conn.close()

    return render_template("change_passwd.html")

#Edit tags

@app.route("/edit_tags", methods=["GET", "POST"])
def create():
if request.method == "POST":
    movie=request.form['movie']
    option=request.form['option']
    username=session['username']
    tag=request.form['tag']
    # Check if tag match the type we want
    if not re.fullmatch(r'[a-zA-Z0-9 ]*', tag):
        flash("Invalid character(s) in your tag!",  "danger")
        return redirect("/edit_tags")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # whether user exists
        cursor.execute("SELECT userid FROM users WHERE username=%s", (username,))
        result1 = cursor.fetchone() 
        if result1==None:
            flash("User does not exist",  "danger")
            return redirect("/")
        userid=result1[0]
        # whether movie exists
        cursor.execute("SELECT movieid FROM movies WHERE title=%s", (movie,))
        result2 = cursor.fetchone() 
        if result2==None:
            flash("Movie does not exist",  "danger")
            return redirect("/edit_tags")
        movieid=result2[0]
        if option == "add":
            # whether tag already exists
            cursor.execute("SELECT COUNT(*) FROM tags WHERE userid=%d AND movieid=%d and tag=%s", (userid,movieid,tag))
            result3=cursor.fetchone()
            if result3[0]!=0: 
                flash("Tag already existed",  "danger")
                return return redirect("/edit_tags")
            try:
                # Insert new tag into the database
                cursor.execute("INSERT INTO tags (userid,movieid,tag) VALUES (%d,%d,%s)", (userid,movieid,tag))
                conn.commit()
                flash("Tag created successfully!", "success")
                return redirect("/edit_tags")
            except mysql.connector.Error as err:
                flash(f"Error: {err}", "danger")
            finally:
                cursor.close()
                conn.close()
                return render_template("edit_tags.html")
        elif option == "delete":
            # whether tag exists
            cursor.execute("SELECT COUNT(*) FROM tags WHERE userid=%d AND movieid=%d and tag=%s", (userid,movieid,tag))
            result3=cursor.fetchone()
            if result3[0]==0: 
                flash("Tag never exists",  "danger")
                return return redirect("/edit_tags")
            try:
                # Delete tag into the database
                cursor.execute("DELETE FROM tags WHERE userid=%d AND movieid=%d and tag=%s", (userid,movieid,tag))
                conn.commit()
                flash("Tag deleted successfully!", "success")
                return redirect("/edit_tags")
            except mysql.connector.Error as err:
                flash(f"Error: {err}", "danger")
            finally:
                cursor.close()
                conn.close()
                return render_template("edit_tags.html")
        else:
            flash("Please enter \"add\" or \"delete\"",  "danger")
            return redirect("/edit_tags")
    finally:
        cursor.close()
        conn.close()
return render_template("edit_tags.html")
    
# Signup

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        
        conn = get_db_connection()
        cursor = conn.cursor()

        cur_userid = 0

        if cur_userid == 0:
            cursor.execute("SELECT MAX(userid) FROM users")
            result = cursor.fetchone()
            
            if result[0] is None:
                cur_userid = 300000
            else:
                cur_userid = result[0] + 1
        else: cur_userid = cur_userid + 1


        try:
            cursor.execute("INSERT INTO users (userid, username, password) VALUES (%s, %s, %s)", (cur_userid ,username, hashed_password))
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect("/")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
    
'''
    
'''
