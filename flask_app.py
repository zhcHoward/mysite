#!/usr/bin/env python
import sqlite3
import hashlib
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

app = Flask(__name__)
"""
from_envar() doesn't work on pythonanywhere.com. I don't know why,
because from_envvar() simply calls from_pyfile().
I have set the environment variable correctly,
the output of os.environ['FlaskAppSettings'] is excatly pointing to
the AppSettings.py.
"""
# app.config.from_envvar('FlaskAppSettings', silent=True)
app.config.from_pyfile('AppSettings.py', silent=True)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    # cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
@app.route('/index')
@app.route('/articles')
def index():
    cursor = g.db.execute('select * from articles order by time desc')
    articles = [dict(id=row[0], title=row[1], content=row[2])
                for row in cursor.fetchall()]
    return render_template('index.html', articles=articles)


@app.route('/articles/<id>')
def article(id):
    cur = g.db.execute(
        'select title, content from articles where id = {}'.format(id))
    article = [dict(title=row[0], content=row[1]) for row in cur.fetchall()]
    return render_template('article.html', article=article)


@app.route('/new-article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        g.db.execute(
            'insert into articles (title, content, time) values (?, ?)',
            (request.form['title'],
             request.form['content'])
        )
        g.db.commit()  # save changes
        return redirect(url_for('index'))
    return render_template('new-article.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        hashobj = hashlib.md5()
        hashobj.update(request.form['password'].encode('utf-8'))
        pwd_md5 = hashobj.hexdigest()
        user = query_db(
            "select nickname, email from users where pwd = ?", (pwd_md5,), True)
        if user is None:
            error = "Your nickname or e-mail address" + \
                "doesn't match your password"
        else:
            if request.form['name'] not in [user['nickname'], user['email']]:
                error = "Your nickname or e-mail address" + \
                    "doesn't match your password"
            else:
                session['logged_in'] = True
                session['nickname'] = user[0]
                return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))


@app.route('/new-updates', methods=['GET', 'POST'])
def add_updates():
    if request.method == 'POST':
        query_db(
            'insert into updates (updates) values (?)',
            (request.form['updates'],)
        )
        g.db.commit()
        return redirect(url_for('updates'))
    return render_template('new-updates.html')


@app.route('/updates')
def updates():
    updates = query_db("select * from updates order by time desc")
    return render_template('updates.html', updates=updates)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
