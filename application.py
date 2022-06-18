from flask import Flask


application = Flask(__name__)





@application.route("/index")
@application.route("/")
def index():
    return "index"

@application.route("/about")
def about():
    return "<h1> About website BlogDeploy </h1>"


if __name__ == "__main__":
    application.debug = True
    application.run()
