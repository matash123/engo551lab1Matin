import psycopg2
import csv

conn = psycopg2.connect("host=ec2-52-0-67-144.compute-1.amazonaws.com dbname=d9rbgsmkbh5270 user=ugobzqnheqklpw password=3b428743e124dd0a1f02b89a0373208cd7e7ca39d980d6e0d97b2a7aeae34361")
cur = conn.cursor()
cur.execute('''CREATE TABLE bookssss(
        isbn integer PRIMARY KEY,
        title text,
        author text,
        year integer
)
''')
conn.commit()
with open('books.csv', 'r') as f:
    next(f)
    cur.copy_from(f, 'bookssss', sep=';')

conn.commit()