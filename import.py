import os
import csv

conn = psycopg2.connect("host=ec2-52-0-67-144.compute-1.amazonaws.com dbname=d9rbgsmkbh5270 user=ugobzqnheqklpw password=3b428743e124dd0a1f02b89a0373208cd7e7ca39d980d6e0d97b2a7aeae34361")
cur = conn.cursor()
conn.commit()
with open('books.csv', 'r') as f:
    reader = csv.reader(f)
    next(f)
    for isbn, title, author, year in reader:
        conn.execute ("INSERT INTO booksssss (isbn, title, author, year \
            VALUES (:isbn, :title, :author, :year)", \
                {"isbn":isbn, "title":title, "author":author, "year":year})

conn.commit()

