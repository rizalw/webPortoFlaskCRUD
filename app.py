from flask import Flask, render_template, url_for, redirect, request
import flask_login
import mysql.connector

# Initiate mysqlconnector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="portofoliowebsite"
)
cursor = mydb.cursor()

# Initiate flask_login
login_manager = flask_login.LoginManager()

# Initiate app
app = Flask(__name__)
with open("secret.txt", "r") as secret:
    text = secret.read()
    print(text)
    app.secret_key = text

# Connect flask_login to the main app
login_manager.init_app(app)

# Get registered accounts
cursor.execute("SELECT * FROM accounts")
myresult = cursor.fetchall()

users = {}
for x in myresult:
    users[x[1]] = {'password' : x[2]}

# Prerequisite for using Flask_login
class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user

# Routing
@app.route("/")
def index():
    return render_template("index.html", current_user = flask_login.current_user)

@app.route("/admin")
@flask_login.login_required
def admin():
    return render_template("admin.html", current_user = flask_login.current_user, list_users = users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = request.form['email']
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('index'))

    return 'Bad login'

@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)