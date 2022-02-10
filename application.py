from email import message
from operator import methodcaller
import os
import requests
import statistics


from flask import Flask, session, request, jsonify, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.debug = True
app.config["SECRET_KEY"]= "matt"

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    session["username"] = "admin"
    session["userID"] = 0
    return render_template("index.html")

@app.route("/signup")
def signup():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0;
        message="Username taken"
        return render_template("index.html", url="signup", message=message, page="signup")

    db.execute("INSERT INTO users (username, password) \
		VALUES (:username, :password)", {"username": username, "password": password}) 
    
    print(f"{username} can now be used")
    db.commit()
    return render_template("index.html", name=username)

@app.route("/logout")
def logout():
    name = session["username"]
    session["username"] = "admin"
    session["userID"] = 0
    return render_template("logout.html", name=name)

@app.route("/find", methods=["GET", "POST"])
def find():
    if request.method == "POST":
        username = request.form.get("username")
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        session["username"] = user.username
        session["userID"] = user.id
        
        allBooks = db.execute("SELECT * FROM books").fetchall()
        return render_template("find.html", name=session["username"], allBooks=allBooks)

@app.route("/find/search", methods=["POST"])			
def search():
	book_id = request.form.get("book_id")

	book_id1 = '%' + book_id + '%'
	book_id2 = db.execute("SELECT * FROM books WHERE author LIKE :author \
							OR title LIKE :title OR isbn LIKE :isbn", \
							{"author": book_id1,"title": book_id1,"isbn": book_id1}).fetchall()

	return render_template("search.html", name=session["username"], book_id2=book_id2)

@app.route("/find/search/details", methods=["GET", "POST"])			
def details():
	if request.method == "POST":
		result_id = request.form.get("result_id")
		rating = request.form.get("rating")
		review = request.form.get("review")
		ratingGR = [100,100]

		session["old_reviews"] = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": result_id}).fetchall()

		if result_id is not None:
			result = db.execute("SELECT * FROM books WHERE id = :id", {"id": result_id}).fetchone()
			session["result"] = result
			session["result_id"] = result.id

			# Request API key from GoodReads
			res = requests.get("https://www.goodreads.com/book/review_counts.json", \
					params={"key": GoodReadsAPIKey, "isbns": session["result"].isbn})

			if res.status_code != 200:
			 	return render_template("details.html", result=session["result"], reviews=session["old_reviews"], rating=ratingGR)

			data = res.json()
			print(data)
			session["rating_avg"] = data['books'][0]['average_rating']
			session["rating_number"] = data['books'][0]['work_ratings_count']
			ratingGR = [session["rating_avg"], session["rating_number"]]
						
			return render_template("details.html", result=session["result"], reviews=session["old_reviews"], rating=ratingGR)

		if rating is not None:
			checkDUPLICATE = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id", \
										{"user_id": session["user_ID"],"book_id": session["result_id"]}).rowcount
			if checkDUPLICATE != 0:
				message = "You've already published a review for this book."
				return render_template("error.html", url="details", message=message, page="the book details.")
			else:
				print("Review appended to list.")
				# INSERT into review table
				db.execute("INSERT INTO reviews (rating, submission, book_id, user_id, username) \
			 				VALUES (:rating, :submission, :book_id, :user_id, :username)", \
			 				{"rating":rating, "submission":review, "book_id":session["result_id"], \
			 				"user_id":session["user_ID"], "username":session["username"]})
				db.commit()
				session["old_reviews"] = db.execute("SELECT * FROM reviews WHERE book_id = :id", 
													{"id": session["result_id"]}).fetchall()
				return render_template("details.html", result=session["result"], reviews=session["old_reviews"], rating=ratingGR)

		else:
			return render_template("details.html", result=session["result"], reviews=session["old_reviews"], rating=ratingGR)

	if request.method == "GET":
		ratingGR = [session["rating_avg"], session["rating_number"]]
		return render_template("details.html", result=session["result"], reviews=session["old_reviews"], rating=ratingGR)
   
