from flask import Flask, request, render_template, flash, redirect, url_for, session
import os
import re
from functools import wraps
from peewee import *
from cryptography.fernet import Fernet
from passlib.hash import sha256_crypt
from datetime import datetime

app = Flask(__name__, static_folder=os.path.abspath('your/project/folder/static'))
app.secret_key = 'super secret keysdhsagdhashsaj213hjhdsfkj6l43lks'

db = PostgresqlDatabase(
    'yourdbname',
    user='yourdbusername',
    password='yourdbpassword',
    host='localhost')


@app.before_request
def _db_connect():
    db.connect()

    
@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["logged_in"]:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    from forms import LoginForm
    from db_classes import UsersDiary
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        username = login_form.username.data
        password = login_form.password.data
        if not UsersDiary.check_username_exists(username):
            flash("This username does not exist.", "danger")
            return render_template("login.html", login_form=login_form)
        if not sha256_crypt.verify(password, UsersDiary.get_password_of_user(username)):
            flash("Wrong password for username.", "danger")
            return render_template("login.html", login_form=login_form)
        flash("Logged in successfully.", "success")
        session["logged_in"] = username
        return redirect(url_for("index"))
    return render_template("login.html", login_form=login_form)


@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    from forms import SignUpForm
    from db_classes import UsersDiary
    signup_form = SignUpForm(request.form)
    if request.method == "POST" and signup_form.validate():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        key = Fernet.generate_key()
        UsersDiary.insert({
            UsersDiary.username: username,
            UsersDiary.password: sha256_crypt.hash(password),
            UsersDiary.email: email,
            UsersDiary.key: key
        }).execute()
        flash("You have registered successfully.", "success")
        return redirect(url_for("index"))
    return render_template("signup.html", signup_form=signup_form)


@app.route("/write_article")
@login_required
def write_article():
    edit = False
    return render_template("write_article.html", edit=edit)


@app.route("/my_articles")
@login_required
def my_articles():
    return render_template("my_articles.html")


@app.route("/load_articles", methods=['POST', 'GET'])
@login_required
def load_articles():
    from db_classes import Articles
    import json
    articles = {"data":[]}
    for article_info in Articles.articles_of_user(session["logged_in"]):
        articles["data"].append({
                    "ID": article_info.id,
                    "Author": article_info.author,
                    "Name": '<a href="/show_article/' + str(article_info.id) + '">' + article_info.name + '</a>',
                    "Last Edited": article_info.last_edited,
                    "Edit": '<a href="/edit_article/' + str(article_info.id) + '">' +
                   '<span id="edit_button" style="color:blue;" class="glyphicon glyphicon-edit"></span>' +
                 '</a>',
                    "Delete": '<a href="/my_articles">' +
                   '<span onclick="deleteItem(\'' + str(article_info.id) + '\');" id="delete_button" style="color:red;" class="glyphicon glyphicon-trash"></span>' +
                 '</a>'
        })

    return json.dumps(articles)


@app.route('/save_article', methods=['POST', 'GET'])
@login_required
def save_article():
    from db_classes import Articles, UsersDiary
    article_name = request.form.get("name_of_article")
    article_content = request.form.get("article")
    last_edit_date = datetime.now()
    key = UsersDiary.get(UsersDiary.username == session["logged_in"]).key
    cipher_suite = Fernet(key)
    ciphered_content = cipher_suite.encrypt(article_content.encode())
    Articles.insert({Articles.author: session["logged_in"],
                     Articles.name: article_name,
                     Articles.content: ciphered_content,
                     Articles.last_edited: str(last_edit_date)
                     }).execute()
    flash("Article saved successfully.", "success")
    return render_template("index.html")


@app.route('/edit_article/<article_id>')
@login_required
def edit_article(article_id):
    from db_classes import Articles, UsersDiary
    key = UsersDiary.get(UsersDiary.username == session["logged_in"]).key
    cipher_suite = Fernet(key)
    article_name = Articles.get(Articles.id == article_id).name
    try:
        content = re.escape(cipher_suite.decrypt(Articles.get_article(article_id).content.encode()).decode())
        edit = True
        return render_template("write_article.html", edit=edit, article_name=article_name,
                               article_id=article_id, content=content)
    except Exception:
        flash("You are not authorized to do that action.", "danger")
        return redirect(url_for("index"))


@app.route('/complete_edit_article', methods=['GET', 'POST'])
@login_required
def complete_edit_article():
    from db_classes import Articles, UsersDiary
    article_name = request.form.get("name_of_article")
    article_content = request.form.get("article")
    article_id = request.form.get("article_id")
    last_edit_date = datetime.now()
    key = UsersDiary.get(UsersDiary.username == session["logged_in"]).key
    cipher_suite = Fernet(key)
    ciphered_content = cipher_suite.encrypt(article_content.encode())
    Articles.update({Articles.name: article_name,
                     Articles.content: ciphered_content,
                     Articles.last_edited: str(last_edit_date)
                     }).where(Articles.id == article_id).execute()
    flash("Article edited successfully.", "success")
    return render_template("index.html")


@app.route('/delete_article', methods=['GET', 'POST'])
@login_required
def delete_article():
    from db_classes import Articles
    if request.method == "POST":
        data = request.get_json()
        Articles.delete_article(data["id"])
        return "OK"


@app.route('/show_article/<article_id>')
@login_required
def show_article(article_id):
    from db_classes import Articles, UsersDiary
    key = UsersDiary.get(UsersDiary.username == session["logged_in"]).key
    cipher_suite = Fernet(key)
    try:
        article_name = Articles.get(Articles.id == article_id).name
        article_content = (cipher_suite.decrypt(Articles.get_article(article_id).content.encode()).decode())
        return render_template("show_article.html", article_name=article_name, article_content=article_content)
    except Exception:
        flash("You are not authorized to do that action.", "danger")
        return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
