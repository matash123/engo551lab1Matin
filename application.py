Skip to content
Search or jump to…
Pull requests
Issues
Marketplace
Explore
 
@matash123 
 The password you provided is in a list of passwords commonly used on other websites. To increase your security, you must update your password. After February 23, 2022 we will automatically reset your password. Change your password on the settings page.

Read our documentation on safer password practices.

EricaLem
/
project1
Public
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
project1/application.py /
@EricaLem
EricaLem Added /api/<isbn>
Latest commit 3bd9b5c on Feb 27, 2020
 History
 1 contributor
197 lines (160 sloc)  7.29 KB
   
import os
import requests # for access to GoodReads API
import statistics

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session # store session server-side
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

#DATABASE_URL = 'postgres://hszbrtnoxysrwz:f1e4c793c56b123ceb088f2f1175a64d84ce58efc4acc04bbec1d328908fce2e@ec2-34-193-42-173.compute-1.amazonaws.com:5432/d9n3d36eha0ujd'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# the toolbar is only enabled in debug mode:
app.debug = True # disable when done
app.config["SECRET_KEY"] = "enableCookies" # set a 'SECRET_KEY' to enable the Flask session cookies
toolbar = DebugToolbarExtension(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)  # Session created so the user's info can be maintained

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
#engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine)) # sessions for each user

GoodReadsAPIKey = "EApqSumsCZMIrnDlflgQ" 

# Routes

@app.route("/")			
def index():	
	session["username"] = "admin"
	session["user_ID"] = 0		
	return render_template("index.html")

@app.route("/signup")			
def signup():	
	"""Register for website"""		
	return render_template("signup.html")

@app.route("/login")			
def login():
	"""Login to website"""
	return render_template("login.html")

@app.route("/hello", methods=["POST"])			
def hello():
	"""Greetings page for new members"""
	username = request.form.get("username")
	password = request.form.get("password")

	# IF username exists
	if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
		message="Sorry, username already taken."
		return render_template("error.html", url="signup", message=message, page="signup page.")
 
	# OTHERWISE, insert into user table
	db.execute("INSERT INTO users (username, password) \
		VALUES (:username, :password)", {"username": username, "password": password}) 

	print(f"Now {username} is registered.")
	db.commit()
	return render_template("hello.html", name=username)

@app.route("/goodbye")			
def goodbye():
	"""Logout of website"""
	name = session["username"]
	session["username"] = "admin"
	session["user_ID"] = 0
	return render_template("goodbye.html", name=name)

@app.route("/member", methods=["GET", "POST"])			
def member():

	"""Search for a book"""
	if request.method == "POST":
		usrname = request.form.get("username")
		user = db.execute("SELECT * FROM users WHERE username = :username", {"username": usrname}).fetchone()
		session["username"] = user.username
		session["user_ID"] = user.id

		allBooks = db.execute("SELECT * FROM books").fetchall()
		return render_template("member.html", name=session["username"], allBooks=allBooks)

	if request.method == "GET":
		allBooks = db.execute("SELECT * FROM books").fetchall()
		return render_template("member.html", name=session["username"], allBooks=allBooks)

@app.route("/member/search", methods=["POST"])			
def search():
	"""Retrieve responses from search"""
	book_id = request.form.get("book_id")

	book_id1 = '%' + book_id + '%'
	book_id2 = db.execute("SELECT * FROM books WHERE author LIKE :author \
							OR title LIKE :title OR isbn LIKE :isbn", \
							{"author": book_id1,"title": book_id1,"isbn": book_id1}).fetchall()

	return render_template("search.html", name=session["username"], book_id2=book_id2)

@app.route("/member/search/details", methods=["GET", "POST"])			
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

@app.route("/api/<isbn>", methods=["GET", "POST"])
def book_api(isbn):
	"""Return details about a book by its ISBN #."""
	session["isbn"] = isbn
	# Make sure book exists in database
	checkBook = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": session["isbn"]}).rowcount
	bookz = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": session["isbn"]}).fetchone()
	session["bookID"] = bookz.id
	reviewz = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": session["bookID"]}).fetchall()
	reviewCount = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": session["bookID"]}).rowcount
	sum_num = 0
	for i in range(reviewCount):
		ratez = reviewz[i].rating
		sum_num = sum_num + ratez
	avg = sum_num / reviewCount

	if checkBook == 0:
		# Return 404 Error
		return jsonify({"error": "Invalid"}), 422
	else:
		# Get book data
  		return jsonify({
  			"title": bookz.title,
  			"author": bookz.author,
  			"year": bookz.year,
  			"isbn": bookz.isbn,
  			"review_count": reviewCount,
  			"average_score": avg
 			})

if __name__ == '__main__':
	with app.app_context():
		main()
