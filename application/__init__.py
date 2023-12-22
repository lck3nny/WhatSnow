from datetime import timedelta

# Infrastructure Imports
# --------------------------------------------------
from flask import Flask, request, send_from_directory, render_template
import pymysql
import firebase_admin
from firebase_admin import credentials
import google.cloud.logging
import json

# Import Handlers                             Public
# --------------------------------------------------
from .handlers.public.home import HomePageHandler, SearchHandler, ComingSoonHandler
from .handlers.public.accounts import LoginHandler, LogoutHandler, SignupHandler, AccountHandler, ForgotPasswordHandler, UpdateUserDetailsHandler, AddToQuiverHandler, RemoveFromQuiverHandler
from .handlers.public.add_edit import NewImportHandler, ImportDetailsHandler, ImportConfirmationHandler, ImportCompleteHandler, EditSkiboard
from .handlers.public.view import ViewHandler, StartCompareHandler, CompareHandler, AddToCompareHandler, RemoveComparisonHandler, ClearComparisonsHandler

from .handlers.public.learning import LearningHandler

# Import Handlers                              Admin
# --------------------------------------------------
from .handlers.admin.portal import AdminPortalHandler, AdminViewUsersHandler


# Initialise app
# --------------------------------------------------
__author__ = 'liamkenny'
app = Flask(__name__)
app.secret_key = "3537251460"
app.permanent_session_lifetime = timedelta(days=7)


'''
# Database Setup
# --------------------------------------------------
#db = pymysql.connect("localhost", "username", "password", "database")
f = open('config/localdb_config.json')
dbconfig = json.load(f)
db = pymysql.connect(dbconfig['localhost'], dbconfig['username'], dbconfig['password'], dbconfig['database'])
f.close()

def someName():
    cursor = db.cursor()
    sql = "SELECT * FROM table"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template('index.html', results=results)
'''

#logging.basicConfig(filename='record.log', level=logging.DEBUG)


# Init firebase database connection
cred = credentials.Certificate('config/firebase_service_account_key.json')
firebase_admin.initialize_app(cred)

# Init cloud logging
client = google.cloud.logging.Client.from_service_account_json('config/logging_service_account_key.json')
client.setup_logging()

# Run the application
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    #app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# Define static routes 
# --------------------------------------------------
@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/ads.txt')
def serve_static_files():
    return send_from_directory(app.static_folder, request.path[1:])


# Define error routes 
# --------------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error/404.html', page_name='error'), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error/500.html', page_name='error'), 500
    

# Define public routes
# --------------------------------------------------
app.add_url_rule(rule='/', view_func=HomePageHandler.as_view('home'), methods=['GET'])
app.add_url_rule(rule='/search/', view_func=SearchHandler.as_view('search'), methods=['POST'])

# Accounts
app.add_url_rule(rule='/login/', view_func=LoginHandler.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule(rule='/login/forgot/', view_func=ForgotPasswordHandler.as_view('forgot'), methods=['GET', 'POST'])
app.add_url_rule(rule='/logout/', view_func=LogoutHandler.as_view('logout'), methods=['GET'])
app.add_url_rule(rule='/signup/', view_func=SignupHandler.as_view('signup'), methods=['GET', 'POST'])
app.add_url_rule(rule='/account/', view_func=AccountHandler.as_view('account'), methods=['GET'])
app.add_url_rule(rule='/update-user-details/', view_func=UpdateUserDetailsHandler.as_view('update_details'), methods=['POST'])
app.add_url_rule(rule='/add-to-quiver/', view_func=AddToQuiverHandler.as_view('add_to_quiver'), methods=['POST'])
app.add_url_rule(rule='/remove-from-quiver/', view_func=RemoveFromQuiverHandler.as_view('remove_from_quiver'), methods=['POST'])

# Add / Edit
app.add_url_rule(rule='/import/', view_func=NewImportHandler.as_view('new_import'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<slug>/', view_func=ImportDetailsHandler.as_view('import_details'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<slug>/confirm/', view_func=ImportConfirmationHandler.as_view('import_conf'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<slug>/complete/', view_func=ImportCompleteHandler.as_view('import_complete'), methods=['GET'])
app.add_url_rule(rule='/edit/<slug>/', view_func=EditSkiboard.as_view('edit-skiboard'), methods=['GET'])

# View / Compare
app.add_url_rule(rule='/learn/', view_func=LearningHandler.as_view('learning'), methods=['GET'])
app.add_url_rule(rule='/view/<slug>/', view_func=ViewHandler.as_view('view'), methods=['GET'])
app.add_url_rule(rule='/compare/', view_func=StartCompareHandler.as_view('start_compare'), methods=['GET'])
app.add_url_rule(rule='/compare/<slugs>/', view_func=CompareHandler.as_view('compare'), methods=['GET'])
app.add_url_rule(rule='/add-to-compare/', view_func=AddToCompareHandler.as_view('add-to-compare'), methods=['POST'])
app.add_url_rule(rule='/remove-from-compare/', view_func=RemoveComparisonHandler.as_view('remove-from-compare'), methods=['POST'])
app.add_url_rule(rule='/clear-comparisons/', view_func=ClearComparisonsHandler.as_view('clear-comparisons'), methods=['POST'])

app.add_url_rule(rule='/comingsoon', view_func=ComingSoonHandler.as_view('comingsoon'), methods=['GET'])

# Define admin routes
# --------------------------------------------------
app.add_url_rule(rule='/admin/', view_func=AdminPortalHandler.as_view('admin_portal'), methods=['GET'])
app.add_url_rule(rule='/admin/users/', view_func=AdminViewUsersHandler.as_view('adimin_view_users'), methods=['GET'])
#app.add_url_rule(rule='/admin/users/', view_func=AdminViewUsersHandler.as_view('adimin_view_users'), methods=['POST'])
app.add_url_rule(rule='/admin/users/<id>/', view_func=AdminViewUsersHandler.as_view('adimin_view_user'), methods=['GET'])

