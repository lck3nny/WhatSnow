import json
import pytz
from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
import pyrebase
from firebase_admin import firestore 

# Model Imports
# --------------------------------------------------
import application.models.user as User

__author__ = 'liamkenny'

f = open('firebase_config.json')
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
        user = db.collection('Users').where('email', '==', email).get()

        if not user:
            # Logging...
            msg = "Logged in user does not exist in firestore: {}\n".format(email)
            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()

            user['fname'] = 'Test'
            user['lname'] = 'User'
        else:
            user = user[0].to_dict()

        # Process successful sign in
        session['user'] = user

        flash('You have been successfully logged in as {} {}'.format(user['fname'], user['lname']), 'info')
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
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()
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

        # Logging...
        msg = "Checking if user exists: {}\n".format(email)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
        f.close()

        # Initialise firestore client
        db = firestore.client()
        existing_user = db.collection('Users').where('email', '==', email).get()
        if existing_user.exists:
            flash('A user already exists with this email address.', 'error')
            return redirect('/signup')

        # Initialise firebase auth connection
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()

        # Logging...
        msg = "Signing up new user: \n{} --- {}".format(email, password)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
        f.close()

        # Create new user
        try:
            user = auth.create_user_with_email_and_password(email, password)
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

        # Complete user object and save in session
        user['f_name'] = fname
        user['l_name'] = lname
        user['email'] = email
        session['user'] = user

        # Logging...
        msg = "New User Created!: \n{}\n".format(json.dumps(user))
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
        f.close()        
    
        # Creating a document using 'add'
        db.collection('Users').add({
            'email': email,
            'fname': user['f_name'],
            'lname': user['l_name'],
            'ski': ski,
            'snowboard': [snowboard, stance],
            'created': datetime.now(pytz.timezone('Canada/Pacific')),
            'updated': datetime.now(pytz.timezone('Canada/Pacific')),
            'permissions': []
            }) 
        
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

        # Logging...
        msg = "Resetting password for: \n{}".format(email)
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
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
        if not 'user' in session:
            return redirect('/login')

        # Initialize firestore client 
        db = firestore.client()
        user = db.collection('Users').where('email', '==', session['user']['email']).get()

        if not user:
            # Logging...
            msg = "User in session does not exist within Firestore: {}\n".format(session['user']['email'])
            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()

            session.pop('user', None)
            return redirect('/login')

        user = user[0].to_dict()

        return render_template('accounts/account.html', session=session, page_name='account', user=user)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# U P D A T E   D E T A I L S          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UpdateUserDetailsHandler(MethodView):
    # -------------------------------------- P O S T
    def post(self):
        if not 'user' in session:
            return redirect('/login')

        # Get firestore user from email
        try:
            user = User.get_user(email=session['user']['email'])
            user_dict = user.to_dict()
        except:
            # Logging...
            msg = "ERROR: Could not get firebase user from email in session\n{}\n".format(session['user'])
            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()
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

        # Logging...
        msg = "Updating  user details...\nOLD Name: {} {}\nNEW Name: {} {}\n".format(user_dict['fname'], user_dict['lname'], update_obj['fname'], update_obj['lname'])
        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
        f.close()

        # Update the user details
        success, user = User.update_user(user.id, update_obj)
        if not success:
            # Logging...
            msg = "ERROR - Could not update user details\n{}\n".format(e)
            f = open("logs.txt", "a")
            f.write("{}\nLOGGING... {}\n\n".format(datetime.now(pytz.timezone('Canada/Pacific')), msg))
            f.close()
            flash('We could not update your details. Please try again.')
        else:
            session.pop('user', None)
            session['user'] = user.to_dict()
            flash('Details successfully updated')
            
        
        return redirect('/account')
