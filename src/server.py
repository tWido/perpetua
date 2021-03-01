from flask import Flask, request
import json
import mysql.connector

from .config import DB_USER, DB_PWD, DB_URL

app = Flask(__name__)

# TODO - schools by distance
# TODO - compute ratings on startup and cache, on post review recompute and resort


@app.route('/schools')
def schools():
    conditions, order_by, limit, offset = parse_query_params(request.args)
    return get_from_db('schools', conditions, order_by, limit, offset)


@app.route('/schools/<int:school_id>')
def school_by_id(school_id):
    return get_from_db('schools', conditions=[('id', school_id)])


@app.route('/schools/info/<int:school_id>')
def school_info_by_id(school_id):
    return get_from_db('school_info', conditions=[('school_id', school_id)])


@app.route('/reviews')
def reviews():
    conditions, order_by, limit, offset = parse_query_params(request.args)
    return get_from_db('reviews', conditions, order_by, limit, offset)


@app.route('/reviews/<int:review_id>')
def review_by_id(review_id):
    return get_from_db('reviews', conditions=[('id', review_id)])


@app.route('/review/add/<string:token>', methods=['GET', 'POST'])
def create_review(token):
    if request.method == 'POST':
        return add_review(token)
    else:
        return validate_token(token)


def add_review(token):
    # TODO
    return 'Not yet implemented'


def validate_token(token):
    # TODO
    return 'Not yet implemented'


def parse_query_params(request_args):
    conditions = []
    order_by = None
    limit = None
    offset = None
    for arg in request_args:
        if arg == 'order_by':
            order_by = request_args.get(arg)
            continue
        if arg == 'limit':
            limit = request_args.get(arg)
            continue
        if arg == 'offset':
            offset = request_args.get(arg)
            continue
        cond = (arg, request_args.get(arg))
        conditions.append(cond)
    return conditions, order_by, limit, offset


def create_query(table, conditions=None, order_by=None, limit=None, offset=None):
    query = 'SELECT * FROM ' + table

    params = []
    if conditions:
        query = query + ' WHERE '
        first = True
        for col_name, value in conditions:
            if not allowed_column_name(table, col_name):
                continue
            if not first:
                query = query + ' AND '
                first = False
            query = query + col_name + ' = %s '
            params.append(value)

    if order_by:
        if allowed_column_name(table, order_by):
            query = query + ' ORDER BY ' + order_by

    if limit and limit.isnumeric():
        query = query + ' LIMIT ' + limit

    if offset and offset.isnumeric():
        query = query + ' OFFSET ' + offset

    return query, tuple(params)


def get_from_db(table_name, conditions=None, order_by=None, limit=None, offset=None):
    dbc = get_db_connection()
    cursor = dbc.cursor()
    query, params = create_query(table_name, conditions, order_by, limit, offset)
    cursor.execute(query, params)
    row_headers = [x[0] for x in cursor.description]  # extract column names
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(row_headers, row)))
    return json.dumps(results) if len(results) != 1 else json.dumps(results[0])


def get_db_connection():
    # TODO - connection pool
    return mysql.connector.connect(user=DB_USER, password=DB_PWD, host=DB_URL, database='perpetua')


def release_db_connection(connection):
    connection.close()


def allowed_column_name(table, column_name):
    # TODO -  list of allowed column names
    return True
