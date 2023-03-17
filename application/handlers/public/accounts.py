import json
import pytz
from datetime import datetime
import logging

# Infrastructure Imports
# --------------------------------------------------
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
import pyrebase
from firebase_admin import firestore 

# Model Imports
# --------------------------------------------------
import application.models.user as User

__author__ = 'liamkenny'

f = open('config/firebase_config.json')
firebase_config = json.load(f)
f.close()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# L O G I N                            H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LoginHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if 'user' in session:
            return redirect('/account')

        return render_template('accounts/login.html', session=session, page_name='login')

    # -------------------------------------- P O S T
    def post(self):
        if 'user' in session:
            return redirect('/account')
             
        # Get user info
        email = request.form.get('email', 'error@problem.com')
        password = request.form.get('password', 'password')
        if not email or not password:
            flash('You must provide an email and password to sign in!', 'error')
            return redirect('/login')

        # Initialise firebase auth connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
    
        # Sign in user
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_info = auth.get_account_info(user ['idToken'])
            user['info'] = user_info
            user['email'] = email
        
        # Catch unsuccessful sign in 
        except:
            flash('No account found with this username and password.', 'error')
            return redirect('/login')         
 
        # Initialise firestore client
        db = firestore.client()
        user = db.collection('Users').where('email', '==', email).get()[0]

        if not user:
            logging.warning("Logged in user does not exist in firestore: {}".format(email))
            flash('No users found with those credentials. Please try again.')
            return redirect('/login')
        else:
            # Process successful sign in
            logging.info("User successfully logged in:\n{}".format(user))
            session['user'] = user.to_dict()
            session['user']['id'] = user.id


        flash('You have been successfully logged in as {} {}'.format(session['user']['fname'], session['user']['lname']), 'info')
        return redirect('/account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# L O G O U T                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LogoutHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if 'user' in session: 
            flash('You have been successfully logged out.', 'info')
            session.pop('user', None)

        return redirect('/')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S I G N U P                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SignupHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if 'user' in session:
            msg = "User already in session - redirecting}"
            logging.info("Redirecting...\nUser already signed in: {}".format(session['user']['email']))
            return redirect('/account')
        
        return render_template('accounts/signup.html', session=session, page_name='signup')

    # -------------------------------------- P O S T
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
        if existing_user.exists:
            flash('A user already exists with this email address.', 'error')
            return redirect('/signup')

        # Initialise firebase auth connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Create new user
        try:
            logging.info("Signing up new user: \n{} --- {}".format(email, password))
            auth.create_user_with_email_and_password(email, password)
            # auth.send_email_verification(user['idToken'])
        except Exception as e:
            # ToDo...
            # Handle different firebase resposnes

            msg = "ERROR: \n{}\n".format(e)
            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()
            flash('There was an issue creating your account.', 'error')
            return redirect('/signup')
    
        # Creating a document using 'add'
        user = db.collection('Users').add({
            'email': email,
            'fname': fname,
            'lname': lname,
            'ski': ski,
            'snowboard': [snowboard, stance],
            'created': datetime.now(pytz.timezone('Canada/Pacific')),
            'updated': datetime.now(pytz.timezone('Canada/Pacific')),
            'permissions': []
            }) 

        logging.info("New Firestore User Created: \n{}\n".format(json.dumps(user)))     

        session['user'] = user.to_dict()
        session['user']['id'] = user.id
        
        # Creating document using a 'document reference'
        '''
        db.collection('Users').document().set({
            'email': email,
            'fname': user['f_name'],
            'lname': user['l_name'],
            'ski': ski,
            'snowboard': [snowboard, stance]
            })
        '''

        # Adding additional info at a later date
        '''
        id = 'abc'
        db.collection('Users').document(id).set({'biker': True}, merge = True)
        '''
        

        return redirect('/account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# F O R G O T   P W D                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForgotPasswordHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if 'user' in session:
            return redirect('/account')

        return render_template('accounts/password_reset.html', session=session, page_name='password_reset')

    # -------------------------------------- P O S T
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A C C O U N T                        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AccountHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if not 'user' in session:
            return redirect('/login')

        # Initialize firestore client 
        db = firestore.client()
        user = db.collection('Users').document(session['user']['id']).get()

        if not user:
            logging.warning("User in session does not exist within Firestore: {}\n".format(session['user']['email']))
            session.pop('user', None)
            return redirect('/login')

        session['user'] = user.to_dict()
        session['user']['id'] = user.id

        return render_template('accounts/account.html', session=session, page_name='account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# U P D A T E   D E T A I L S          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UpdateUserDetailsHandler(MethodView):
    # -------------------------------------- P O S T
    def post(self):
        if not 'user' in session:
            return redirect('/login')

        # Get firestore user from id
        try:
            user = User.get_user(id=session['user']['id'])
            user_dict = user.to_dict()
        except:
            logging.error("Could not get firebase user from email in session\n{}\n".format(session['user']))
            flash("There was a problem updating your user info")
            return redirect('/account')
        
        # Populate update object with form values
        update_obj = {
            'fname': request.form.get('fname'),
            'lname': request.form.get('lname')
        }
        
        # Prevent updates if not required
        if not update_obj['fname'] and not update_obj['lname']:
            flash('You must enter a name to update.')
            return redirect('/account')
        
        if update_obj['fname'] == user_dict['fname'] and update_obj['lname'] == user_dict['lname']:
            flash('No updates were made to your account')
            return redirect('/account')

        # Update the user details
        logging.info("Updating  user details...\nOLD Name: {} {}\nNEW Name: {} {}\n".format(user_dict['fname'], user_dict['lname'], update_obj['fname'], update_obj['lname']))
        user, error = User.update_user(user.id, update_obj)
        if error:
            logging.error("Could not update user details\n{}\n".format(error))
            flash('We could not update your details. Please try again.')
        else:
            session.pop('user', None)
            session['user'] = user.to_dict()
            session['user']['id'] = user.id
            flash('Details successfully updated')
            
        return redirect('/account')
