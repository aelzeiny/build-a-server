import requests
from flask import Flask, render_template, jsonify, request
from flask_mysqldb import MySQL
from contextlib import closing

app = Flask(__name__,
            template_folder='../front-end/build',
            static_folder='../front-end/build/static')
mysql = MySQL()

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DB'] = 'fur_real'

mysql.init_app(app)


def validate_cat_picture(url):
    assert requests.head(url).status_code == 200


@app.route("/")
def template_test():
    return render_template('index.html')


@app.route('/cats', methods=['GET'])
def index():
    with closing(mysql.connection.cursor()) as cur:
        cur.execute('SELECT id, name, url FROM cats')
        results = cur.fetchall()
    return jsonify(results)


@app.route('/cats', methods=['POST'])
def create():
    cat_params = request.json
    if 'name' not in cat_params or 'age' not in cat_params or 'url' not in cat_params:
        return jsonify(message='Not enough information to register a cat'), 400
    if len(cat_params['url']) > 255:
        return jsonify(message='URL too long'), 400
    try:
        validate_cat_picture(cat_params['url'])
    except (requests.exceptions.InvalidURL, requests.exceptions.HTTPError, AssertionError):
        return jsonify(message='Cannot access cat picture'), 400
    with closing(mysql.connection.cursor()) as cur:
        cur.execute(
            'INSERT INTO cats (name, age, url) VALUES (%(name)s, %(age)s, %(url)s)',
            {'name': cat_params['name'], 'age': cat_params['age'], 'url': cat_params['url']}
        )
    return jsonify({**cat_params, 'id': cur.lastrowid})


@app.route('/cat/<idx>', methods=['GET'])
def show(idx):
    with closing(mysql.connection.cursor()) as cur:
        cur.execute('SELECT id, name, age, url FROM cats WHERE id = %(idx)s', dict(idx=int(idx)))
        cat = cur.fetchone()
    if cat is None:
        jsonify(message='Cat not found'), 404
    return jsonify(cat)


@app.route('/cat/<idx>', methods=['PATCH'])
def update(idx):
    cat_params = request.json
    if 'name' not in cat_params or 'age' not in cat_params or 'url' not in cat_params:
        return jsonify(message='Not enough information to update a cat'), 400
    if len('url') > 255:
        return jsonify(message='URL too long'), 400
    try:
        validate_cat_picture(cat_params['url'])
    except (requests.exceptions.InvalidURL, requests.exceptions.HTTPError, AssertionError):
        return jsonify(message='Cannot access cat picture'), 404

    with closing(mysql.connection.cursor()) as cur:
        cur.execute(
            'UPDATE cats SET name = %(name)s, age = %(age)s, url = %(url)s WHERE id = %(idx)s',
            {'name': cat_params['name'], 'age': cat_params['age'], 'url': cat_params['url'], 'idx': idx}
        )
    return jsonify({'id': cur.lastrowid, **cat_params})


@app.route('/cat/<idx>', methods=['DELETE'])
def destroy(idx):
    with closing(mysql.connection.cursor()) as cur:
        cur.execute('SELECT id, name, age, url FROM cats WHERE id = %(idx)s', dict(idx=idx))
        cat = cur.fetchone()
        if cat is None:
            jsonify(message='Cat not found'), 404
        cur.execute('DELETE FROM cats WHERE id = %(idx)s', dict(idx=idx))
    return jsonify(cat)


if __name__ == '__main__':
    app.run()
