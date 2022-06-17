import sqlite3
import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort, g, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin
                 

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


app.register_blueprint(admin, url_prefix='/admin')


login_manager = LoginManager(app)


login_manager.login_view = 'login'
login_manager.login_message = "Login to access restricted pages"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Helper function for creating database tables"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    """DB connection if not already established"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Establishing a database connection before executing a query"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Close the connection to the database if it was established"""
    if hasattr(g, 'link_db'):
        g.link_db.close()



@app.route("/")
def index():
 
    return render_template('index.html', menu = dbase.getMenu(), posts=dbase.getPostsAnonce())



@app.route("/add_post", methods=["POST", "GET"])
def addPost():

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('ERROR  of add post', category='error')
            else:
                flash('Post added successfully', category='success')
        else:
            flash('ERROR  of add post', category='error')

    return render_template('addpost.html', menu=dbase.getMenu(), title="Add post")


@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)


@app.route("/login", methods=["POST", "GET"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('profile'))


    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
 
            return redirect(request.args.get("next") or url_for("profile"))  

        flash("Invalid pair username/password ", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Authorization", form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.psw.data)
            res = dbase.addUser(form.name.data, form.email.data, hash)


            if res:
                flash("You have successfully registered", "success")
                return redirect(url_for('login'))
            else:
                flash("Error adding to database", "error")


    return render_template("register.html", menu=dbase.getMenu(), title="Registration", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are logged out", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Account")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Avatar update error", "error")
                flash("Avatar updated", "success")
            except FileNotFoundError as e:
                flash("File read error", "error")
        else:
            flash("Avatar update error", "error")

    return redirect(url_for('profile'))


if __name__ == "__main__":
    application.debug = True  
    app.run(host='0.0.0.0', port=5000)


