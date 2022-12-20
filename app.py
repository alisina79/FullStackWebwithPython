from flask import Flask, render_template, url_for, request, redirect, flash, session

#flask with small f represents the library itself
#Flask with capital F shows the instance/instance varible for the libray
#render_template is used to return one html file at a time
#url_for is used to return the page as well but automatically. 
#WTForms includes (passwordfield, emailfield, textfield)
#passlib , a library for password. 
#encryption, decryption  (sha256_crypt) 
from wtforms import Form, StringField, EmailField, PasswordField, validators, TextAreaField
from passlib.hash import sha256_crypt
#import mysql.connector
#from mysql import flask_mysqldb
from flask_mysqldb import MySQL, MySQLdb

app = Flask(__name__)
app.secret_key = '123456789'


#Flask(__name__) instance function. 
#parameter __name__ is passed through the instance function

mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'post_data'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)



@app.route('/') #it creates a path for the page on the browser
def home(): #function which returns
	return render_template('home.html') #using render_template fun, you return one html page at a time

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')


@app.route('/team')
def team():
	return render_template('team.html')

class RegisterFrom(Form):
	name = StringField('Name', [validators.length(min=3, max=40)])
	username = StringField('Username', [validators.length(min=3, max=20)])
	email = EmailField('Email', [validators.Email(), validators.length(min=3, max=20)])
	password = PasswordField('Passsword', [validators.length(min=5)])

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterFrom(request.form)

	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		email = form.email.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#cursor class
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(Name, Username, Email, Password) VALUES(%s, %s,%s,%s)", (name, username, email, password))
		mysql.connection.commit()
		cur.close()

		flash('You are regsitered. ', 'success')

		return redirect(url_for('home'))

	return render_template('register.html', form=form)

class LoginForm(Form):
	username = StringField('Username', [validators.length(min=3, max=20)])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # GEt user form
        username = form.username.data
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            # Get stored value
            data = cur.fetchone()
            password = data['Password']
            # Compare password
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                flash('Incorrect password', 'danger')
                return render_template('login.html', form=form)

        else:
            flash('Username not found', 'danger')
            # Close connection
            cur.close()
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/dashboard')
def dashboard():
	cur = mysql.connection.cursor()
	result = cur.execute("SELECT * from posts")
	posts = cur.fetchall()

	return render_template('dashboard.html', posts=posts)


class PostForm(Form):
	title = StringField('Title', [validators.length(min=5, max=200)])
	body = TextAreaField('Body', [validators.length(min=50)])



@app.route('/addpost', methods=['GET', 'POST'])
def addpost():
	form = PostForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		#cursor class
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO posts(title, body, author) VALUES(%s, %s,%s)", (title, body, session['username']))
		mysql.connection.commit()
		cur.close()

		flash('your post is published. ', 'success')

		return redirect(url_for('dashboard'))

	return render_template('addpost.html', form=form)

@app.route('/logout')
def logout():
	cur = mysql.connection.cursor()
	session.clear()
	flash('you are logged out','success')
	return redirect(url_for('home'))

@app.route('/post/<string:id>/')
def post(id):
	cur = mysql.connection.cursor()
	result=cur.execute("SELECT * from posts where id=%s", [id])
	post = cur.fetchone()
	return render_template("post.html", post=post)

if __name__ == '__main__':
	app.run(debug=True)


#Vistual Studio C++ 2015, 2017
#Database Connectivity 
#Form, type of forms (WTForms)
# password, encrypted (unreadable ) - passlib
#MYSQL, flask-mysqldb, mysql-connector

#render_field 
