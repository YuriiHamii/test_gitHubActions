from flask import Flask, render_template, request, flash, session, redirect, url_for, abort


application = Flask(__name__)


application.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hxg6h7f'


menu = [{"name": "Downloading", "url": "install-flask"},
        {"name": "First application", "url": "first-app"},
        {"name": "Feedback", "url": "contact"}]


@application.route("/")
def index():
    return render_template('index.html', menu=menu)

@application.route("/about")
def about():
    return render_template('about.html', title="About website", menu=menu)


@application.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == 'POST':
        print(request.form)
        print(request.form['username'])
       
        if len(request.form['username']) > 2:
            flash('message sent successfully', category='success')
        else:
            flash('message sending error', category='error')
            

    return render_template('contact.html', title="Feedback", menu = menu)



@application.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)

    return f"User profile: {username}"



@application.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' and request.form['username'] == "selfedu" and request.form['psw'] == "123":
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)


@application.errorhandler(404)

def pageNotFount(error):
    return render_template('page404.html', title="Page not found", menu=menu), 404



if __name__ == "__main__":
    application.debug = True
    application.run()
