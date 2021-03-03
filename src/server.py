import flask
import json
import re
from datetime import datetime
from flask import Flask

from .db_connection import get_db_connection, release_db_connection, allowed_column_name
from.config import RATED

app = Flask(__name__)


@app.route('/schools')
def schools():
    conditions, order_by, limit, offset = parse_query_params(flask.request.args)
    select = None
    if order_by == 'distance':
        user_lat = float(flask.request.args.get('user_lat'))
        user_lon = float(flask.request.args.get('user_lon'))
        # ST_Distance computes distance between two point, but doesn't take world curvature in account
        # correctly working function ST_Distance_Sphere is not implemented in MariaDB, so we use simpler version
        # since backend is meant for small country in Europe
        select = ' *, ST_Distance(point({}, {}), point(latitude, longitude)) as distance '.format(user_lat, user_lon)

    return json.dumps(get_from_db('schools', conditions, order_by, limit, offset, select))


@app.route('/schools/<int:school_id>')
def school_by_id(school_id):
    return get_from_db('schools', conditions=[('id', school_id)])


@app.route('/schools/info/<int:school_id>')
def school_info_by_id(school_id):
    return json.dumps(get_from_db('school_info', conditions=[('school_id', school_id)]))


@app.route('/schools/ratings/<int:school_id>')
def ratings_by_school_id(school_id):
    select = 'school_id '
    for key in RATED:
        col_name = 'rating_' + key
        select = select + ', count({}) as count_{}, avg({}) as avg_{}'.format(col_name, col_name, col_name, col_name)

    res = get_from_db('reviews', conditions=[('school_id', school_id)], select=select)
    res = res[0]
    # mysql returns values as Decimal('value'), which json cannot convert
    for key in res:
        if 'avg' in key:
            res[key] = float(res[key]) if res[key] else None

    return json.dumps(res)


@app.route('/reviews')
def reviews():
    conditions, order_by, limit, offset = parse_query_params(flask.request.args)
    res = get_from_db('reviews', conditions, order_by, limit, offset)
    # mysql return datetime, which json cannot convert
    for review in res:
        review['created'] = str(review['created'])
        review.pop('token_id')
    return json.dumps(res)


@app.route('/reviews/<int:review_id>')
def review_by_id(review_id):
    res = get_from_db('reviews', conditions=[('id', review_id)])
    for review in res:
        review['created'] = str(review['created'])
        review.pop('token_id')
    return json.dumps(res)


@app.route('/reviews/add/<string:token>', methods=['GET', 'POST'])
def create_review(token):
    if flask.request.method == 'POST':
        return add_review(token)
    else:
        return validate_token(token)


def check_range(value, min_val, max_val):
    if not value or value < min_val or value > max_val:
        return None
    return value


def add_review(token):
    dbc = get_db_connection()
    cursor = dbc.cursor()
    query, params = create_query('tokens', conditions=[('token', token)])
    cursor.execute(query, params)
    row = cursor.fetchone()

    if row:
        row_headers = [x[0] for x in cursor.description]
        db_token = dict(zip(row_headers, row))
        school_id = db_token.get('school_id')
        valid_till = db_token.get('valid_till')
        uses = db_token.get('uses')
        token_id = db_token.get('id')
        if uses == 0 or (valid_till is not None and valid_till < datetime.now()):
            status_code = flask.Response(status=401)
            release_db_connection(dbc)
            return status_code

        completed = check_range(flask.request.json.get('completed'), 0, 1)
        pros = flask.request.json.get('pros')
        cons = flask.request.json.get('cons')
        nick = flask.request.json.get('nick')
        time_attended = flask.request.json.get('time_attended')
        created = datetime.now()

        query = 'INSERT INTO reviews (school_id, time_attended, completed, nick, created, pros, cons, token_id'
        values = 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s'
        params = (school_id, time_attended, completed, nick, created, pros, cons, token_id)
        for key in RATED:
            value = check_range(flask.request.json.get('rating_' + key), 0, 10)
            params = params + (value, )
            query = query + ', rating_' + key
            values = values + ', %s'

        query = query + ') ' + values + ')'
        cursor.execute(query, params)

        query = 'UPDATE tokens SET uses = uses - 1 WHERE id = %s '
        cursor.execute(query, (token_id, ))
        dbc.commit()

        status_code = flask.Response(status=201)

    else:
        status_code = flask.Response(status=401)

    release_db_connection(dbc)
    return status_code


def validate_token(token):
    token = get_from_db('tokens', conditions=[('token', token)])

    if token:
        token = token[0]
        valid_till = token.get('valid_till')
        uses = token.pop('uses')
        if uses > 0 and (not valid_till or valid_till > datetime.now()):
            token['valid_till'] = str(token['valid_till'])
            return json.dumps(token)

    status_code = flask.Response(status=401)
    return status_code


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


def create_query(table, conditions=None, order_by=None, limit=None, offset=None, select=None):
    select = '*' if not select else re.sub('[^a-zA-Z0-9_()* ,]', '', select)
    query = 'SELECT ' + select + ' FROM ' + table

    params = []
    if conditions:
        first = True
        for col_name, value in conditions:
            if not allowed_column_name(table, col_name):
                continue
            if first:
                query = query + ' WHERE '
                first = False
            else:
                query = query + ' AND '

            query = query + col_name + ' = %s '
            params.append(value)

    if order_by:
        if allowed_column_name(table, order_by):
            query = query + ' ORDER BY ' + order_by

    if limit and limit.isnumeric():
        query = query + ' LIMIT ' + limit
        if offset and offset.isnumeric():
            query = query + ' OFFSET ' + offset

    print(query)
    return query, tuple(params)


def get_from_db(table_name, conditions=None, order_by=None, limit=None, offset=None, select=None):
    dbc = get_db_connection()
    cursor = dbc.cursor(buffered=True)
    query, params = create_query(table_name, conditions, order_by, limit, offset, select)
    cursor.execute(query, params)
    row_headers = [x[0] for x in cursor.description]  # extract column names
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(row_headers, row)))
    return results
