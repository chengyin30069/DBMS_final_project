from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import hashlib
import re # for detecting tags
import time # for timestamp
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
            return redirect("/home")
        
        else:
            flash("Invalid username or password.", "danger")

        
        # Close the connection
        cursor.close()
        conn.close()

        
    return render_template("login.html")

# Welcome Page

@app.route("/home")
def home():
    if 'username' not in session:
        return redirect("/")
    return render_template("home.html")

@app.route("/my_tags", methods=["GET", "POST"])
def my_tags():
    if 'username' not in session:
        return redirect("/")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    username = session['username']

    cursor.execute("SELECT userid FROM users WHERE username = %s", (username, ))
    userid = cursor.fetchone()

    if not userid:
        return redirect("/")

    try:
        cursor.execute("SELECT tag, tags.movieid, title, timestamp FROM tags, movies WHERE userid=%s AND tags.movieid=movies.movieid", (userid))
        tags=cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template("my_tags.html", tags=tags)


@app.route("/my_ratings", methods=["GET", "POST"])
def my_ratings():
    if 'username' not in session:
        return redirect("/")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    username = session['username']

    cursor.execute("SELECT userid FROM users WHERE username = %s", (username, ))
    userid = cursor.fetchone()

    if not userid:
        return redirect("/")

    try:
        cursor.execute("SELECT rating, ratings.movieid, title, timestamp FROM ratings, movies WHERE userid=%s AND ratings.movieid=movies.movieid", (userid))
        ratings=cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template("my_ratings.html", ratings=ratings)

# Movie Page
@app.route("/movie", methods=["GET", "POST"])
def movie():
    if 'username' not in session:
        return redirect("/")
    search_query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if search_query:  # If there is a search query, filter movies by title
            query = "SELECT title, mv.movieid, avg_rating, genres FROM(SELECT movieid, title, genres FROM movies WHERE title LIKE %s)AS mv, total_ratings WHERE mv.movieid=total_ratings.movieid"
            cursor.execute(query, (f"%{search_query}%",))
        else:
            cursor.execute("SELECT title, mv.movieid, avg_rating, genres FROM (SELECT movieid, title, genres FROM movies ORDER BY RAND( ) LIMIT 10)AS mv, total_ratings WHERE mv.movieid=total_ratings.movieid")
    
        movies = cursor.fetchall()

    finally:
        cursor.close()
        conn.close

    return render_template("movie.html", movies=movies)

@app.route("/404")
def not_found():
    if 'username' not in session:
        return redirect("/")
    return render_template("404.html")

@app.route('/movie/<int:movieid>')
def movie_details(movieid):
    # Connect to the database

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Query to fetch the movie details by movieid
        movie_query = "SELECT movieid, title, avg_rating, genres, imdbid, tmdbid FROM(SELECT title, movieid, genres FROM movies WHERE movieid = %s)AS mv, (SELECT avg_rating FROM total_ratings WHERE movieid = %s)AS t_rt, (SELECT imdbid, tmdbid FROM links WHERE movieid = %s)AS lk"
        cursor.execute(movie_query, (movieid, movieid, movieid))
        movie = cursor.fetchone()  # Fetch the single movie record
        
        #Get tags
        tags_query = "SELECT DISTINCT tag FROM tags WHERE movieid = %s"
        cursor.execute(tags_query, (movieid, ))
        tags = [row['tag'] for row in cursor.fetchall()]
        
    finally:
        cursor.close()
        conn.close()

    # If the movie is not found, return a 404 page
    if not movie:
        return redirect("/404")

    movie['tags'] = tags

    # Pass the movie details to the frontend
    return render_template('movie_page.html', movie=movie)

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
                return redirect("/home")
            else:
                flash("Invalid old password or new password is not identical.", "danger")
        
        else:
            flash("Invalid old password or new password is not identical.", "danger")
        
        cursor.close()
        conn.close()

    return render_template("change_passwd.html")

# add tags (Last page should be "/movies/{movieid}")

@app.route("/add_tags/<int:movieid>", methods=["GET", "POST"])
def add_tags():
    if 'username' not in session:
        return redirect("/")
    if request.method == "POST":
        username=session['username']
        tag=request.form['tag']
        # Check if tag match the type we want
        if not re.fullmatch(r'[a-zA-Z0-9 ]*', tag):
            flash("Invalid character(s) in your tag!",  "danger")
            return redirect(url_for("add_tags",movieid=movieid))
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
            cursor.execute("SELECT COUNT(*) FROM movies WHERE movieid=%s", (movieid,))
            result2 = cursor.fetchone() 
            if result2[0]==0:
                flash("Movie does not exist",  "danger")
                return redirect("/movie")
            # whether tag already exists
            cursor.execute("SELECT COUNT(*) FROM tags WHERE userid=%s AND movieid=%s and tag=%s", (userid,movieid,tag))
            result3=cursor.fetchone()
            if result3[0]!=0: 
                flash("Tag already existed",  "danger")
                return redirect(url_for("/add_tags",movieid=movieid))
            # Insert new tag into the database
            timestamp=int(time.time())
            cursor.execute("INSERT INTO tags (userid,movieid,tag,timestamp) VALUES (%s,%s,%s,%s)", (userid,movieid,tag,timestamp))
            conn.commit()
            flash("Tag created successfully!", "success")
            return redirect(url_for("/add_tags",movieid=movieid))
        finally:
            cursor.close()
            conn.close()
            return render_template("add_tags.html",movieid=movieid)
            
    return render_template("add_tags.html",movieid=movieid)
    
#Edit tags (Last page should be "/my_tags")

@app.route("/edit_tags/{bigint:timestamp}", methods=["GET", "POST"])
def edit_tags():
    if 'username' not in session:
        return redirect("/")
    if request.method == "POST":
        username=session['username']
        tag=request.form['tag']
        # Check if tag match the type we want
        if not re.fullmatch(r'[a-zA-Z0-9 ]*', tag):
            flash("Invalid character(s) in your tag!",  "danger")
            return redirect(url_for("/edit_tags",timestamp=timestamp))
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
            # whether tag exists
            cursor.execute("SELECT COUNT(*) FROM tags WHERE userid=%s AND timestamp=%s", (userid,timestamp))
            result3=cursor.fetchone()
            if result3[0]==0: 
                flash("Tag does not exist",  "danger")
                return redirect("/my_tags")
            try:
                # edit tag into the database (update timestamp)
                new_timestamp=int(time.time())
                cursor.execute("""
                    UPDATE tags
                    SET tag=%s,timestamp=%s
                    WHERE userid=%s AND timestamp=%s
                """, (tag,new_timestamp,userid,timestamp))
                conn.commit()
                flash("Tag edited successfully!", "success")
                return redirect("/my_tags")
            except mysql.connector.Error as err:
                flash(f"Error: {err}", "danger")
                return render_template("edit_tags.html",timestamp=timestamp)
        finally:
            cursor.close()
            conn.close()
    return render_template("edit_tags.html",timestamp=timestamp)

#delete tags (Last page should be "/my_tags")

@app.route("/delete_tags/{bigint:timestamp}", methods=["GET"])
def delete_tags():
    if 'username' not in session:
        return redirect("/")
    username=session['username']
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
        # whether tag exists
        cursor.execute("SELECT COUNT(*) FROM tags WHERE userid=%s AND timestamp=%s", (userid,timestamp))
        result3=cursor.fetchone()
        if result3[0]==0: 
            flash("Tag does not exist",  "danger")
            return redirect("/my_tags")
        try:
            # Delete tag into the database
            cursor.execute("DELETE FROM tags WHERE userid=%s AND timestamp=%s", (userid,timestamp))
            conn.commit()
            flash("Tag deleted successfully!", "success")
            return redirect("/my_tags")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
            return render_template("delete_tags.html",timestamp=timestamp)
    finally:
        cursor.close()
        conn.close()
    return render_template("delete_tags.html",timestamp=timestamp)
    
# add ratings (Last page should be "/movies/{movieid}")

@app.route("/add_ratings/<int:movieid>", methods=["GET", "POST"])
def add_ratings():
    if 'username' not in session:
        return redirect("/")
    if request.method == "POST":
        username=session['username']
        rating=request.form['rating']
        # Check if rating on [0,5]
        if not ((0<=rating<=5) and ((rating*10)%5)==0):
            flash("Invalid rating!",  "danger")
            return redirect(url_for("/add_ratings",movieid=movieid))
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
            cursor.execute("SELECT COUNT(*) FROM movies WHERE movieid=%s", (movieid,))
            result2 = cursor.fetchone() 
            if result2[0]==0:
                flash("Movie does not exist",  "danger")
                return redirect("/movie")
            # whether rating already exists
            cursor.execute("SELECT COUNT(*) FROM ratings WHERE userid=%s AND movieid=%s", (userid,movieid))
            result3=cursor.fetchone()
            if result3[0]!=0: 
                flash("rating already existed",  "danger")
                return redirect(url_for("/movies",movieid=movieid))
            # Insert new rating into the database
            cursor.execute("INSERT INTO ratings (userid,movieid,rating) VALUES (%s,%s,%s)", (userid,movieid,rating))
            conn.commit()
            flash("rating created successfully!", "success")
            return redirect(url_for("/movies",movieid=movieid))
        finally:
            cursor.close()
            conn.close()
    return render_template("add_ratings.html",movieid=movieid)
    
#Edit ratings (Last page should be "/my_ratings")

@app.route("/edit_ratings/{int:movieid}", methods=["GET", "POST"])
def edit_ratings():
    if 'username' not in session:
        return redirect("/")
    if request.method == "POST":
        username=session['username']
        rating=request.form['rating']
        # Check if rating on [0,5]
        if not ((0<=rating<=5) and ((rating*10)%5)==0):
            flash("Invalid rating!",  "danger")
            return redirect(url_for("/edit_ratings",movieid=movieid))
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
            cursor.execute("SELECT COUNT(*) FROM movies WHERE movieid=%s", (movieid,))
            result2 = cursor.fetchone() 
            if result2[0]==0:
                flash("Movie does not exist",  "danger")
                return redirect("/movie")
            # whether rating already exists
            cursor.execute("SELECT COUNT(*) FROM ratings WHERE userid=%s AND movieid=%s", (userid,movieid))
            result3=cursor.fetchone()
            if result3[0]==0: 
                flash("rating does not exist",  "danger")
                return redirect("/my_ratings")
            try:
                # edit rating into the database
                cursor.execute("""
                    UPDATE ratings
                    SET rating=%s
                    WHERE userid=%s AND movieid=%s
                """, (rating,userid,movieid))
                conn.commit()
                flash("rating edited successfully!", "success")
                return redirect("/my_ratings")
            except mysql.connector.Error as err:
                flash(f"Error: {err}", "danger")
                return render_template("edit_ratings.html",movieid=movieid)
        finally:
            cursor.close()
            conn.close()
    return render_template("edit_ratings.html",movieid=movieid)

#delete ratings (Last page should be "/my_ratings")

@app.route("/delete_ratings/{int:movieid}", methods=["GET"])
def delete_ratings():
    if 'username' not in session:
        return redirect("/")
    username=session['username']
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
        cursor.execute("SELECT COUNT(*) FROM movies WHERE movieid=%s", (movieid,))
        result2 = cursor.fetchone() 
        if result2[0]==0:
            flash("Movie does not exist",  "danger")
            return redirect("/movie")
        # whether rating already exists
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE userid=%s AND movieid=%s", (userid,movieid))
        result3=cursor.fetchone()
        if result3[0]==0: 
            flash("rating does not exist",  "danger")
            return redirect("/my_ratings")
        try:
            # Delete rating into the database
            cursor.execute("DELETE FROM ratings WHERE userid=%s AND movieid=%s", (userid,movieid))
            conn.commit()
            flash("rating deleted successfully!", "success")
            return redirect("/my_ratings")
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
            return render_template("delete_ratings.html",movieid=movieid)
    finally:
        cursor.close()
        conn.close()
    return render_template("delete_ratings.html",movieid=movieid)

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
