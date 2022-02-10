import psycopg2
import csv

conn = psycopg2.connect("host=ec2-52-0-67-144.compute-1.amazonaws.com dbname=d9rbgsmkbh5270 user=ugobzqnheqklpw password=3b428743e124dd0a1f02b89a0373208cd7e7ca39d980d6e0d97b2a7aeae34361")
cur = conn.cursor()

cur.execute('''
CREATE TABLE "books"(
    "isbn" TEXT,
    "title" TEXT,
    "author" TEXT,
    "year" TEXT,
    id SERIAL PRIMARY KEY
)
''')

cur.execute('''
CREATE TABLE "reviews"(
    "isbn" TEXT,
    "username" TEXT,
    "rating" FLOAT,
    "review" TEXT,
    id SERIAL PRIMARY KEY
)
''')

cur.execute('''
CREATE TABLE "users"(
    id SERIAL PRIMARY KEY,
    "email" TEXT UNIQUE NOT NULL,
    "password" TEXT NOT NULL
)
''')

with open('books.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        print(row)
        isbn=row[0]
        title=row[1]
        author=row[2]
        year=row[3]
        cur.execute('''INSERT INTO books(isbn,title,author,year)
            VALUES (%s,%s,%s,%s)''',(isbn,title,author,year))

conn.commit()

