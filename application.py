import sqlite3
import os
from flask import Flask, render_template, request, flash, session, redirect, url_for, abort, g
from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

application = Flask(__name__)


application.config.from_object(__name__)
application.config.update(dict(DATABASE=os.path.join(application.root_path, 'flsite.db')))

def connect_db():
    conn = sqlite3.connect(application.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with application.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    '''Start - Connection with DB'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db



@application.teardown_appcontext
def close_db(error):
    '''Close - Connection with DB'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@application.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu = dbase.getMenu(), posts=dbase.getPostsAnonce())


@application.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('ERROR  of add post', category='error')
            else:
                flash('Post added successfully', category='success')
        else:
            flash('ERROR  of add post', category='error')

    return render_template('addpost.html', menu=dbase.getMenu(), title="Add post")


@application.route("/post/<int:id_post>")
def showPost(id_post):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)



if __name__ == "__main__":
    application.run(debug=True)




# Test
# http://127.0.0.1:5000/add_post - 200 -  "GET /add_post HTTP/1.1"
#                      /add_post - 200 =       /add_post
