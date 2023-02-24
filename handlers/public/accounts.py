from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
import pyrebase
import json

__author__ = 'liamkenny'

f = open('fb_config.json')
firebase_config = json.load(f) 
f.close()

'''
msg = "Firebase Auth: ({})\n\n{}".format(type(firebase_config), firebase_config)
f = open("logs.txt", "a")
f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
f.close()
'''
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
        # Get user info
        email = request.form.get('email', 'error@problem.com')
        password = request.form.get('password', 'password')
        if not email or not password:
            flash('You must provide an email and password to sign in!', 'error')
            return redirect('/login')

        # Initialise firebase connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
    
        # Sign in user
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_info = auth.get_account_info(user ['idToken'])
            user['info'] = user_info
        # Catch unsuccessful sign in 
        except:
            flash('No account found with this username and password.', 'error')
            return redirect('/login')         
 
        # Process successful sign in
        flash('You have been successfully logged in as {} {}'.format(user['fname'], user['lname']), 'info')
        user['fname'] = 'Test'
        user['lname'] = 'User'
        session['user'] = user
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

            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
            f.close()
            return redirect('/account')
        
        return render_template('accounts/signup.html', session=session, page_name='signup')

    # -------------------------------------- P O S T
    def post(self):
        # Get user info
        email = request.form.get('email', 'error@problem.com')
        password = request.form.get('password', 'password')
        if not email or not password:
            flash('You must provide an email and password to sign up!', 'error')
            return redirect('/signup')

        # Initialise firebase connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Logging...
        msg = "Signing up new user: \n{} --- {}".format(email, password)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()

        # Create new user
        try:
            user = auth.create_user_with_email_and_password(email, password)
            # auth.send_email_verification(user['idToken'])
        except:
            flash('There was an issue creating your account.', 'error')
            return redirect('/login')

        # Logging...
        msg = "New User Created!: \n{}".format(user)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()

        # Redirect user to account
        user['fname'] = request.form.get('fname', 'Test')
        user['lname'] = request.form.get('lname', 'User')
        session['user'] = user

        return redirect('/account')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# F O R G O T   P W D                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ForgotPasswordHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        return render_template('accounts/password_reset.html', session=session, page_name='password_reset')

    # -------------------------------------- P O S T
    def post(self):
        # Get user's email
        email = request.form.get('email')
        if not email:
            flash('There was an issue collecting your email, please try again.', 'error')
            return redirect('/login/forgot')
    
        # Initialise firebase connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Logging...
        msg = "Resetting password for: \n{}".format(email)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()

        # Reset user password
        try:
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
        if 'user' in session:
            return render_template('accounts/account.html', session=session, page_name='account')
        
        return redirect('/login')
