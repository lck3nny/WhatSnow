import json
import pytz
from datetime import datetime
import logging

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.models.user import User
from app.models.skiboard import SkiBoard

# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
import pyrebase
from firebase_admin import firestore 



__author__ = 'liamkenny'

f = open('config/firebase_config.json')
firebase_config = json.load(f)
f.close()



# V A L I D A T E   E M A I L                  F U N C T I O N
# ------------------------------------------------------------
def validateEmail(email):
    email_chars = ['@', '.']
    for char in email_chars:
        if not char in email:
            return False
        
    return True


# V A L I D A T E   P A S S W O R D            F U N C T I O N
# ------------------------------------------------------------
def validatePassword(password):
    if len(password) < 1:
        return False
    
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# L O G I N                                      H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LoginHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if 'user' in session:
            return redirect('/account')

        return render_template('accounts/login.html', session=session, page_name='login', comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(self):
        if 'user' in session:
            return redirect('/account')
             
        # Get user info
        email = request.form.get('email', 'error@problem.com')
        password = request.form.get('password', 'password')
        if not validateEmail(email) or not validatePassword(password):
            flash('You must provide an email and password to sign in!', 'error')
            return redirect('/login')

        # Initialise firebase auth connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
    
        # Sign in user
        try:
            firebaseuser = auth.sign_in_with_email_and_password(email, password)
            firebaseuser_info = auth.get_account_info(firebaseuser ['idToken'])
            firebaseuser['info'] = firebaseuser_info
            firebaseuser['email'] = email
            logging.info("Firebase User Found: {}".format(firebaseuser))
        
        # Catch unsuccessful sign in 
        except:
            flash('No account found with this username and password.', 'error')
            return redirect('/login')         
 
        # Get User from DB
        user = User.get(id=firebaseuser['localId'], email=email)

        if not user:
            logging.warning("Logged in user does not exist in database: {}".format(email))
            flash('No users found with those credentials. Please try again.')
            return redirect('/login')
        else:
            # Process successful sign in
            logging.info("User successfully logged in:\n{}".format(user))
            session['user'] = user.__dict__


        flash('You have been successfully logged in as {} {}'.format(session['user']['fname'], session['user']['lname']), 'info')
        return redirect('/account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# L O G O U T                                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LogoutHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if 'user' in session: 
            flash('You have been successfully logged out.', 'info')
            session.pop('user', None)

        return redirect('/')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S I G N U P                                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SignupHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if 'user' in session:
            msg = "User already in session - redirecting}"
            logging.info("Redirecting...\nUser already signed in: {}".format(session['user']['email']))
            return redirect('/account')
        
        return render_template('accounts/signup.html', session=session, page_name='signup', comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(self):
        if 'user' in session:
            return redirect('/account')

        # Get user info
        fname = request.form.get('fname', 'Test')
        lname = request.form.get('lname', 'User')
        email = request.form.get('email')
        password = request.form.get('password')
        conf = request.form.get('password2')
        ski = request.form.get('ski', False)
        snowboard = request.form.get('snowboard', False)
        stance = request.form.get('goofyref', False)
        

        # Validate form data
        if not email or not password:
            flash('You must provide an email and password to sign up!', 'error')
            return redirect('/signup')
        elif password != conf:
            flash('Your passwords do not match.', 'error')
            return redirect('/signup')


        # Initialise firestore client
        logging.info("Checking if user exists: {}\n".format(email))
        db = firestore.client()
        existing_user = db.collection('Users').where('email', '==', email).get()

        if existing_user:
            logging.info("Existing User: {}".format(existing_user))
            flash('A user already exists with this email address.', 'error')
            return redirect('/login')

        # Initialise firebase auth connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Create new Firebase user
        try:
            logging.info("Signing up new user: \n{} --- {}".format(email, password))
            firebaseuser = auth.create_user_with_email_and_password(email, password)
            # auth.send_email_verification(user['idToken'])
        except Exception as e:
            # ToDo...
            # Handle different firebase resposnes
            logging.error("Error creating account:\n{}".format(e))
            flash('There was an issue creating your account.', 'error')
            return redirect('/signup')
    
        # Create new DB User
        try:
            user = User(firebaseuser['localId'], fname, lname, email)
            user.save()
        except Exception as e:
            logging.error(f"Unable to create DB user from Firebase user:\n{firebaseuser}")

        logging.info("Created new user: {}".format(user.__dict__))
        session['user'] = user.__dict__

        return redirect('/account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# F O R G O T   P W D                            H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForgotPasswordHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if 'user' in session:
            return redirect('/account')

        return render_template('accounts/password_reset.html', session=session, page_name='password_reset', comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(self):
        if 'user' in session:
            return redirect('/account')

        # Get user's email
        email = request.form.get('email')
        if not email:
            flash('There was an issue collecting your email, please try again.', 'error')
            return redirect('/login/forgot')
    
        # Initialise firebase connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Reset user password
        try:
            logging.info("Resetting password for: \n{}".format(email))
            auth.send_password_reset_email(email)
        except:
            flash('There was an issue resetting your password, please try again.', 'error')
            return redirect('/login/forgot')

        flash('Check your email for a password reset link.', 'info')
        return redirect('/login')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A C C O U N T                                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AccountHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if not 'user' in session:
            return redirect('/login')
        
        # Initialize firestore client 
        # db = firestore.client()
        # user = db.collection('Users').document(session['user']['id']).get()
        #user, quiver = User.get_user(id=session['user']['id'], quiver=True)
        user = User.get(id=session['user']['id'])

        if not user:
            logging.warning("User in session does not exist within Firestore: {}\n".format(session['user']['email']))
            session.pop('user', None)
            return redirect('/login')
        
        session['user'] = user.__dict__
        #session['user']['id'] = user.id

        return render_template('accounts/account.html', session=session, page_name='account', comparisons=SkiBoard.calc_comparisons())

