import psycopg2

hostname = 'ec2-52-0-67-144.compute-1.amazonaws.com'
database = 'd9rbgsmkbh5270'
username = 'ugobzqnheqklpw'
pwd = '3b428743e124dd0a1f02b89a0373208cd7e7ca39d980d6e0d97b2a7aeae34361'
port_id = '5432'
conn = None
cur = None

try: 
    conn = psycopg2.connect(
        host = hostname,
        dbname = database,
        user = username,
        password = pwd,
        port = port_id)

    cur = conn.cursor()

    create_script = ''' CREATE TABLE books (
                            isbn    int PRIMARY KEY,
                            title   varchar(60) NOT NULL,
                            author  varchar(60) NOT NULL,
                            year int))'''
    cur.execute(create_script)

except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()