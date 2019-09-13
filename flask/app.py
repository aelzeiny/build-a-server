import requests
from flask import Flask, render_template, jsonify
from flask_mysqldb import MySQL
from contextlib import closing

app = Flask(__name__,
            # this is the folder where we can find HTML or Jinja2 Templates
            template_folder='../front-end/build',
            # This is the folder we can find the static files built by the front-end (JS, images, and CSS)
            static_folder='../front-end/build/static')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_DB'] = 'fur_real'

mysql = MySQL(app)


def validate_cat_picture(url):
    assert requests.head(url).status_code == 200


@app.route('/')
def template_test():
    return render_template('index.html')


@app.route('/cats', methods=['GET'])
def index():
    with closing(mysql.connection.cursor()) as cur:
        cur.execute('SELECT * FROM cats')
        results = cur.fetchall()
    return jsonify(results)


if __name__ == '__main__':
    app.run(port=5000)
