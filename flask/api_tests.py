import pytest
import requests
from contextlib import closing

from MySQLdb import connect, cursors

server_url = 'http://localhost:5000'
mysql = connect(host='localhost',
                user='root',
                password='',
                database='fur_real',
                port=3306,
                cursorclass=cursors.DictCursor)


@pytest.fixture(autouse=True)
def mysql_conn():
    with closing(mysql.cursor()) as conn:
        conn.execute('INSERT INTO cats (id, name, url, age) SELECT 5000, name, url, age FROM cats LIMIT 1')
        conn.connection.commit()
        yield
        conn.execute('DELETE FROM cats WHERE id=5000')
        conn.connection.commit()


def test_server_is_up():
    response = requests.get(server_url)
    assert response.status_code == 200, 'Request must succeed'
    assert response.headers['Content-Type'].lower() == 'text/html; charset=utf-8'


def test_list_cats(mysql_conn):
    response = requests.get(server_url + '/cats')
    assert response.status_code == 200, 'Request must succeed'
    assert 'application/json' in response.headers['Content-Type'], 'Response body must be a JSON'
    data = response.json()
    assert isinstance(data, list), 'Response is a json list'
    assert len(data) != 0, 'There are some cats in our seeded data'
    assert 'id' in data[0] and 'name' in data[0] and 'url' in data[0], 'Our JSON has the id, name, and url fields'
    assert len(data[0]) == 3, 'Our JSON has ONLY 3 fields. No unnecessary info'


def test_create_cat():
    cat_json = {
        'id': 10001,
        'name': 'that cat over there',
        'age': 200,
        'url': 'https://static2.cbrimages.com/wordpress/wp-content/uploads/2019/09/Garfieldheader.jpg?q=50&fit=crop&w=798&h=407'
    }
    response = requests.post(server_url + '/cats', json=cat_json)
    assert response.status_code == 200, 'Request must succeed'
    assert 'application/json' in response.headers['Content-Type'], 'Response body must be a JSON'

    data = response.json()
    assert isinstance(data, dict), 'Response is a json dictionary'
    assert 'id' in data and 'url' in data and 'name' in data and 'age' in data, 'Cat is returned back after creation'
    assert len(data) == 4, 'No weird keys in data apart from id, url, name, and age!'
    assert data['id'] != 10001, 'I should not be able to specify the ID'

    response = requests.post(server_url + '/cats', json={k: cat_json[k] for k in cat_json if k != 'name'})
    assert response.status_code == 400, 'There should not be enough information to make a cat...'
    data = response.json()
    assert 'message' in data and data['message'] == 'Not enough information to register a cat', 'error message needed'
    assert requests.post(server_url + '/cats', json={**cat_json, 'url': 'this-is-not-a-url.com'}).status_code != 200, \
           'URL must be valid & reachable!'
    assert requests.post(server_url + '/cats', json={**cat_json, 'url': 'a' * 257}).status_code != 200, \
           'URL is longer than 255 characters!'


def test_show_cat(mysql_conn):
    response = requests.get(server_url + '/cat/5000')
    assert response.status_code == 200, 'Request must succeed'
    assert 'application/json' in response.headers['Content-Type'], 'Response body must be a JSON'
    data = response.json()
    assert isinstance(data, dict), 'Response is a json dictionary'
    assert 'id' in data and 'url' in data and 'name' in data and 'age' in data, 'Cat is returned back after creation'

    # SQL injection attack!!!
    requests.get(server_url + '/cat/";TRUNCATE%20TABLE%20cats')
    requests.get(server_url + '/cat/;TRUNCATE%20TABLE%20cats')
    requests.get(server_url + "/cat/';TRUNCATE%20TABLE%20cats")
    assert len(requests.get(server_url + '/cats').json()) != 0, 'You must not be vulnerable to SQL injection!!!'


def test_update_cat(mysql_conn):
    new_cat = requests.get(server_url + '/cat/5000').json()
    new_cat['name'] = 'pretty kitty'
    response = requests.patch(server_url + '/cat/5000', json=new_cat)
    assert response.status_code == 200, 'Request must succeed'
    assert 'application/json' in response.headers['Content-Type'], 'Response body must be a JSON'
    cat = response.json()
    assert isinstance(cat, dict), 'Response is a json dictionary'
    assert 'id' in cat and 'url' in cat and 'name' in cat and 'age' in cat, 'Cat is returned back after creation'
    assert cat == new_cat


def test_destroy_cat(mysql_conn):
    response = requests.delete(server_url + '/cat/5000')
    assert response.status_code == 200, 'Request must succeed'
    assert 'application/json' in response.headers['Content-Type'], 'Response body must be a JSON'
    data = response.json()
    assert isinstance(data, dict), 'Response is a json dictionary'
    assert requests.get(server_url + '/cat/5000').status_code == 404, 'Please blacklisted cat.'
