import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])

with conn.cursor() as cur:
    cur.execute("SELECT * FROM disorders")
    res = cur.fetchall()
    conn.commit()
    print(res)