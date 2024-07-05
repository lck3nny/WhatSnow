from datetime import timedelta

# Infrastructure Imports
# --------------------------------------------------
from flask import Flask, request, send_from_directory, render_template
import firebase_admin
from firebase_admin import credentials
import google.cloud.logging
#from elasticsearch import Elasticsearch
from app.core import db

# Import Handlers                             Public
# --------------------------------------------------
from .handlers.public.home import HomePageHandler, SearchHandler, ComingSoonHandler
from .handlers.public.advanced_search import AdvancedSearchHandler
from .handlers.public.accounts import LoginHandler, LogoutHandler, SignupHandler, AccountHandler, ForgotPasswordHandler
from .handlers.public.add_edit import NewImportHandler, CompleteImportHandler, EditSkiboard
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

# Connect SQL Alchemy
# mysql+<drivername>://<username>:<password>@<server>:<port>/dbname
'''
# Configuring database URI
user = "root"
pwd = "password"
host = "localhost"
db_name = "WhatSnow"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{user}:{pwd}@{host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
'''

'''
# Connect ElasticSearch to application
f = open(os.path.dirname(__file__) + '/../config/bonsai_config.json')
es_config = json.load(f)
app.elasticsearch = Elasticsearch([app.config[es_config['url']]])  \
    if app.config[es_config['url']] else None
'''

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

# Advanced Search
app.add_url_rule(rule='/advanced-search/', view_func=AdvancedSearchHandler.as_view('advanced-search'), methods=['GET', 'POST'])

# Accounts
app.add_url_rule(rule='/login/', view_func=LoginHandler.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule(rule='/login/forgot/', view_func=ForgotPasswordHandler.as_view('forgot'), methods=['GET', 'POST'])
app.add_url_rule(rule='/logout/', view_func=LogoutHandler.as_view('logout'), methods=['GET'])
app.add_url_rule(rule='/signup/', view_func=SignupHandler.as_view('signup'), methods=['GET', 'POST'])
app.add_url_rule(rule='/account/', view_func=AccountHandler.as_view('account'), methods=['GET'])

# Add / Edit
app.add_url_rule(rule='/import/', view_func=NewImportHandler.as_view('new_import'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/complete/', view_func=CompleteImportHandler.as_view('import_details'), methods=['POST'])
app.add_url_rule(rule='/edit/<slug>/', view_func=EditSkiboard.as_view('edit-skiboard'), methods=['GET', 'POST'])

# View / Compare
app.add_url_rule(rule='/learn/', view_func=LearningHandler.as_view('learning'), methods=['GET'])
app.add_url_rule(rule='/view/<slug>/', view_func=ViewHandler.as_view('view'), methods=['GET'])
app.add_url_rule(rule='/compare/', view_func=StartCompareHandler.as_view('start_compare'), methods=['GET'])
app.add_url_rule(rule='/compare/<slugs>/', view_func=CompareHandler.as_view('compare'), methods=['GET'])
app.add_url_rule(rule='/add-to-compare/', view_func=AddToCompareHandler.as_view('add-to-compare'), methods=['POST'])
app.add_url_rule(rule='/remove-from-compare/', view_func=RemoveComparisonHandler.as_view('remove-from-compare'), methods=['POST'])
app.add_url_rule(rule='/clear-comparisons/', view_func=ClearComparisonsHandler.as_view('clear-comparisons'), methods=['POST'])

# Other
app.add_url_rule(rule='/comingsoon', view_func=ComingSoonHandler.as_view('comingsoon'), methods=['GET'])

# Define admin routes
# --------------------------------------------------
app.add_url_rule(rule='/admin/', view_func=AdminPortalHandler.as_view('admin_portal'), methods=['GET'])
app.add_url_rule(rule='/admin/users/', view_func=AdminViewUsersHandler.as_view('adimin_view_users'), methods=['GET'])
#app.add_url_rule(rule='/admin/users/', view_func=AdminViewUsersHandler.as_view('adimin_view_users'), methods=['POST'])
app.add_url_rule(rule='/admin/users/<id>/', view_func=AdminViewUsersHandler.as_view('adimin_view_user'), methods=['GET'])

