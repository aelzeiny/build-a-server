const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const path = require('path');
const mysqlClient = require('mysql');
const axios = require('axios');

const port = 5000;

// Set-up middlewares in express. These are JS functions that intercept every request/response
// This one serves up the static files generated by our front-end
app.use('/static', express.static(path.join(__dirname, '/../front-end/build/static/')));
// This one makes it so that we can receive JSON from API calls.
app.use(bodyParser.json());

const mysql = mysqlClient.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'fur_real'
});

const query = function(sql, args) {
    return new Promise((success, error) => {
        mysql.query(sql, args, (err, rows) => {
            if (err) return error(err);
            success(rows);
        });
    });
};

app.get('/', (req, res) => {
    return res.sendFile(path.join(path.join(__dirname + '/../front-end/build/index.html')));
});

app.get('/cats', (req, res) => {
    query('SELECT id, name, url FROM cats').then(data => res.json(data));
});

app.post('/cats', (req, res) => {
    if (!(req.body.name && req.body.age && req.body.url)) {
        res.status(400);
        return res.json({message: 'Not enough information to register a cat'});
    }
    const {name, age, url} = req.body;
    if (url > 255) {
        res.status(400);
        return res.json({message: 'URL too long'});
    }

    axios.head(url).then(() => {
        query('INSERT INTO cats SET ?', {name, age, url}).then((data) => {
            res.json({id: data.insertId, name, age, url});
        });
    }).catch(() => {
        res.status(400);
        return res.json({message: 'URL is not valid'});
    });
});

app.get('/cat/:id', (req, res) => {
    query('SELECT id, name, age, url FROM cats WHERE id = ?', [req.params.id]).then(data => {
        if (!data || data.length === 0) {
            res.status(404);
            return res.json({message: 'Cat not found'});
        }
        return res.json(data[0]);
    });
});

app.patch('/cat/:id', (req, res) => {
    if (!(req.body.name && req.body.age && req.body.url)) {
        res.status(400);
        return res.json({message: 'Not enough information to update a cat'});
    }
    const {name, age, url} = req.body;
    if (url > 255) {
        res.status(400);
        return res.json({message: 'URL too long'});
    }
    axios.head(url).then(() => {
        query('UPDATE cats SET name = ?, age = ?, url = ? WHERE id = ?', [name, age, url, req.body.id])
            .then(() => {
                res.json({id: req.body.id, name, age, url})
            });
    }).catch(() => {
        res.status(400);
        return res.json({message: 'URL is not valid'});
    });

});

app.delete('/cat/:id', (req, res) => {
    query('SELECT id, name, age, url FROM cats WHERE id = ?', [req.params.id]).then(data => {
        if (!data || data.length === 0) {
            res.status(404);
            return res.json({message: 'Cat not found'});
        }
        query('DELETE FROM cats WHERE id = ?', [req.params.id]).then(() => {
            return res.json(data[0]);
        });
    });
});


app.listen(port, () => console.log(`Example app listening on port ${port}!`));
