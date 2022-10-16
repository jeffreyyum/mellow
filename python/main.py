import logging
import os
import psycopg2
import psycopg2.extras
from psycopg.errors import ProgrammingError
import json
from flask import Flask, jsonify, request

def exec_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            row = cur.fetchone()
            conn.commit()
            if row: print(row[0])
    except ProgrammingError:
        return

conn = psycopg2.connect(os.environ["DATABASE_URL"])

with conn.cursor() as cur:
    cur.execute("SELECT * FROM disorders")
    res = cur.fetchall()
    conn.commit()
    print(res)

app = Flask(__name__)

# Create a cursor and initialize psycopg
pg_conn_string = os.environ["DATABASE_URL"]

connection = psycopg2.connect(pg_conn_string)

# Set to automatically commit each statement
connection.set_session(autocommit=True)

cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def db_get_all():
    cursor.execute("SELECT * FROM disorders")
    results = cursor.fetchall()
    return results


def db_get_by_name(name):
    cursor.execute('SELECT * FROM specialists WHERE name = %s', (name, ))
    result = cursor.fetchone()
    return result


def db_filter_listings(disorder):
    cursor.execute(
        'SELECT * FROM specialists WHERE disorder = %s',
        (disorder, ))
    result = cursor.fetchall()
    return result


def db_create_specialist(disorder, name, num):
    cursor.execute(
        "INSERT INTO specialists (disorder, name, num) VALUES (%s, %s, %s)",
        (disorder, name, num))
    result = cursor.fetchall()
    return result


def db_delete_listing(name):
    cursor.execute("DELETE FROM specialists WHERE name = %s RETURNING name", (name, ))
    result = cursor.fetchall()
    return result


# Routes!
@app.route('/', methods=['GET'])
def index():
    return jsonify(db_get_all())


@app.route("/<id>", methods=['GET'])
def get_by_name(name):
    specialist = db_get_by_name(name)
    if not specialist:
        return jsonify({"error": "invalid name", "code": 404})
    return jsonify(specialist)


@app.route("/search", methods=['GET'])
def filter_listings():
    result = db_filter_listings(int(request.args.get('min_year')),
                                request.args.get('group'))
    return jsonify(result)


@app.route("/", methods=['POST'])
def create_specialist():
    new_specialist = request.json
    try:
        res = db_create_specialist(new_specialist['disorder'], new_specialist['name'],
                               new_specialist['num'])
        return jsonify(res)

    except Exception as e:
        return jsonify({"error": str(e)})

app.run(host="0.0.0.0", debug=True)