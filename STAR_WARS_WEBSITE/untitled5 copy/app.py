import csv
from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, EqualTo
from forms import SignUpForm, loginForm, check_account, User, passwordForgotForm, resetPassForm
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_bcrypt import bcrypt
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = "hello"
#for email

app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'soen287starwars@gmail.com'
app.config['MAIL_PASSWORD'] = 'SOEN287!'
app.config['MAIL_DEFAULT_SENDER'] = 'soen287starwars@gmail.com'


#app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_USERNAME'] = 'soen287starwars@gmail.com'
#app.config['MAIL_PASSWORD'] = 'SOEN287!'
#app.config['MAIL_DEFAULT_SENDER'] = 'soen287starwars@gmail.com'


mail = Mail()
mail.init_app(app)

#Login manger stuff
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = find_user(user_id)
    if user:
        user.password = None
    return user

def find_user(email):
    with open('data/userCsv.csv') as f:
        for user in csv.reader(f):
            if email == user[0]:
                return User(*user)
    return None
login_manager.login_view="login"

#home page route
@app.route('/')
def home():
    return render_template("homePageTemplate.html")

#eras page route
@app.route('/eras')
@login_required
def eras():
    return render_template("erasPageTemplate.html")


#acyual sign up page
@app.route('/Register', methods=['GET', 'POST'])
def signUp():
    form=SignUpForm()
    if form.validate_on_submit():
           user=find_user(form.email.data)
           if not user:
                #salt = bcrypt.gensalt()
                #password = bcrypt.hashpw(form.password.data.encode(), salt)
                with open('data/userCsv.csv', 'a') as f:
                    writer= csv.writer(f)
                    writer.writerow([form.email.data, form.password.data])#password.decode()
                flash('Registered successfully.')
                return redirect('/login')
           else:
                flash('This username already exists, choose another one')
    return render_template('SignUpTemplate.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form=loginForm()
    if form.validate_on_submit():
        user = find_user(form.email.data)
        email=form.email.data
        if check_account(form.email.data, form.password.data):
        #if user and bcrypt.checkpw(form.password.data.encode(), user.password.encode()):
            login_user(user)
            #result={form.email.data:form.password.data}
            flash('Logged in successfully')
            next_page = session.get('next', '/')
            session['next'] = '/'
            #link = url_for('character', email=form.email.data)
            return render_template('userTemplate.html', password=form.password.data, email=form.email.data)#, link=link)
        else:
            flash('Incorrect username/password')
    return render_template("loginTemplate.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/character', methods=['GET', 'POST'])
@login_required
def character():


    name=request.form['name']
    side=request.form['side']
    kyber=request.form['kyber']
    race=request.form['race']
    with open('data/userCharacters.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([name, side, kyber, race])
    flash('Character created successfully.')
    return redirect('/displayChar')

@app.route('/displayChar', methods=['GET', 'POST'])
@login_required
def displayChar(email):
    charList=[]
    with open('data/userCsv.csv', newline="") as f:
        reader = list(csv.reader(f))
        for row in reader:
            for field in row:
                if field == email:
                    charList.append(row)
    return render_template('displayChar.html', list=charList)

#forgot password
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form=passwordForgotForm()
    if form.validate_on_submit():
        email=form.email.data
        user = find_user(email)
        if user:
            msg = Message("Password Reset", recipients=[form.email.data])
            #link = render_template('resetPassword.html', form=form, email=email,_external=True )
            link = url_for('resetHandler', email = form.email.data, _external=True)
            msg.body = 'Hello'+email+',\nYou or someone else has requested that a new password be set for your account. If you made this request, then please follow this link'+link
            msg.html = render_template('mail.html',email=email, link=link)
            #return f'<h1>email</h1>'
            mail.send(msg)
            flash("message has been sent to your email!")
    return render_template("forgotPassword.html", form=form)

#actually resets password
@app.route('/resetHandler/<email>', methods=['GET', 'POST'])
def resetHandler(email):
    form = resetPassForm()
    if form.validate_on_submit():
        updatedlist=[]
        currentlist=[]

        with open('data/userCsv.csv', newline="") as f:
            reader=list(csv.reader(f))
            currentlist=reader #copy of data stored

            for row in reader:
                for field in row:
                    if field == email:
                        updatedlist.append(row)
                        newPassword = form.password.data
                        updatedlist[0][1] = newPassword
            for index, row in enumerate(currentlist):
                for field in row:
                    if field == updatedlist[0]:
                        currentlist[index]=updatedlist #replacing old list with current list
            with open('data/userCsv.csv', 'w', newline="") as f:
                writer=csv.writer(f)
                writer.writerows(currentlist)
                flash('password successfully changed!')
            return redirect(url_for('login'))



    return render_template('resetPassword.html', form=form)



#user page
@app.route('/user/<email>')
@login_required
def user(email, password):
  return render_template("userTemplate.html", email=email, password=password)#, link=link)


@app.route('/src')
def src():
    return render_template("sourcesPageTemplate.html")


@app.route('/timeline')
def time():
    return render_template("timelineTemplate.html")


if __name__ == '__main__':
    app.run(debug=True)
