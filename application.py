import os

from hashlib import md5
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Flask objects
app = Flask(__name__)
app.secret_key = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'

# SQL objects
engine = create_engine("postgres://edvpoetkzjshhd:a3f5922084155bf6bd7118c461fb68bc768f975d1e8a1441812f24a4de931d5a@ec2-107-22-211-248.compute-1.amazonaws.com:5432/dediqmbmo9m18i")
db = scoped_session(sessionmaker(bind=engine))

# Flask route
@app.route("/")
def index():
    # Display breif about the web app
    if 'username' in session:
        return render_template('index.html', session=session["username"])
    return render_template("index.html", session=None)

@app.route("/login", methods=["GET"])
def login():
    if 'username' not in session:
        return render_template("login.html")
    else:
        # Display an Error Method not allowed
        return render_template("error.html", error="USERNAME NOT FOUND!")

@app.route("/checkuser", methods=["POST"])
def checkuser():
    name, email, password, count = [None for i in range(4)]
    print(request.form)
    if "login" in request.form:
        name = request.form.get("logname")
        password = request.form.get("logpassword").encode('utf-8')
        password = md5(password).hexdigest()

    elif "signup" in request.form:
        name = request.form.get("signame")
        email = request.form.get("signemail")
        password = request.form.get("signpassword").encode('utf-8')
        password = md5(password).hexdigest()

    if db.execute("SELECT * FROM users WHERE (username=:name AND password=:password) OR email=:email",
            {"name": name, "password": password, "email":email}).rowcount != 0:

        if "login" in request.form:
            session['username'] = name
            return redirect(url_for('search'))
        elif "signup" in request.form:
            # Display an error as user found.
            return render_template('login.html', error='account is already exist!')

    elif "signup" in request.form and db.execute("SELECT username FROM users WHERE username=:name OR email=:email",
            {"name": name, "email": email}).rowcount == 0:
        db.execute("INSERT INTO users VALUES(:name, :email, :password)",
                {"name": name, "email": email, "password": password})
        db.commit()
        # Display sign up is successfully done.
        return render_template('login.html', success="account has been created successfully!")
    else:
        # Display an error for user not found.
        return render_template('login.html', error="user not found!")

@app.route("/search", methods=["GET", "POST"])
def search():
    # Display all books
    books = None
    try:
        if request.method == "GET" and 'username' not in session:
            raise Exception('This method is not allowed!')

        if request.method == "POST":
            if "query" in request.form:
                query = str(request.form.get("query"))
                query = '%'+query+'%'
                books = db.execute("SELECT isbn, title, author, pub_year, img_url, average_score, review_count FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query ORDER BY title ASC",
                    {"query": query})
                if books.rowcount == 0:
                    return render_template("error.html", error="NO MATCH FOUND!")
        else:
            books = db.execute("SELECT isbn, title, author, pub_year, img_url, average_score, review_count FROM books ORDER BY title ASC")
    except Exception as e:
        return render_template("error.html", error="ERROR OCCURED!")

    return render_template("search.html", session=session['username'], username=session['username'], books=books)


@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def book(isbn):
    if 'username' not in session:
        return render_template("error.html", error="PLEASE LOGIN FIRST!")
    query = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    # GET THE REVIEWS FROM DB
    reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchall()

    review_list = []
    for i in range(len(reviews)):
        review_list.append({"review": reviews[i][1], "username": reviews[i][3], "rate": [j for j in range(1, 6)
                if j <= reviews[i][2]]})

    return render_template("book.html", query=query, reviews=review_list)

@app.route("/book/review/<string:isbn>", methods=["POST"])
def review(isbn):
    if 'username' not in session:
        return render_template("error.html", error="PLEASE LOGIN FIRST!")

    review = request.form.get('review')
    rate = 0

    for i in range(1, 6):
        if 's'+str(i) in request.form:
            rate = i

    # SAVE THE REVIEW INTO DB
    check_review = db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND username=:name",
        {"isbn": isbn, "name": session["username"]}).fetchone()

    if check_review is None:
        db.execute("INSERT INTO reviews(isbn, review, rate, username) VALUES(:isbn, :review, :rate, :username)",
            {"isbn": isbn, "review": review, "rate": rate, "username": session["username"]})

        counter = str(db.execute("SELECT review_count FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone())
        avg = str(db.execute("SELECT average_score FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone())

        counter, avg = int(counter[1:-2]), float(avg[1:-2])
        avg = round(((avg*counter) + rate) / (counter+1), 2)

        db.execute("UPDATE books SET review_count=:counter, average_score=:avg WHERE isbn=:isbn", {"counter": counter+1, "avg": avg, "isbn": isbn})
        db.commit()
        return redirect(url_for('book', isbn=isbn))
    else:
        return render_template("error.html", error="YOU HAVE REVIEWED THIS BOOK BEFORE!")

@app.route("/book/api/<string:isbn>")
def api(isbn):

    query = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    if query is None:
        return jsonify({"error": "isbn not found!"})

    return jsonify({
        "title": query.title,
        "author": query.author,
        "year": query.pub_year,
        "isbn": query.isbn,
        "review_count": query.review_count,
        "average_score": query.average_score
    })

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
