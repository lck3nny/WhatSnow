from datetime import timedelta
import logging
from flask import Flask, request, send_from_directory

# Import Handlers
# --------------------------------------------------
from .handlers.public.home import HomePageHandler
from .handlers.public.accounts import LoginHandler, LogoutHandler, SignupHandler, AccountHandler, ForgotPasswordHandler
from .handlers.public.imports import NewImportHandler, ImportDetailsHandler, ImportConfirmationHandler, ImportCompleteHandler
from .handlers.public.view import ViewItemHandler, CompareItemsHandler
from .handlers.public.learning import LearningHandler


__author__ = 'liamkenny'

app = Flask(__name__)
app.secret_key = "3537251460"
app.permanent_session_lifetime = timedelta(days=7)

logging.basicConfig(filename='record.log', level=logging.DEBUG)

if __name__ == '__main__':
    app.run(debug=True)

# Define public routes
# --------------------------------------------------
app.add_url_rule(rule='/', view_func=HomePageHandler.as_view('home'), methods=['GET'])
app.add_url_rule(rule='/login/', view_func=LoginHandler.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule(rule='/login/forgot/', view_func=ForgotPasswordHandler.as_view('forgot'), methods=['GET', 'POST'])
app.add_url_rule(rule='/logout/', view_func=LogoutHandler.as_view('logout'), methods=['GET'])
app.add_url_rule(rule='/signup/', view_func=SignupHandler.as_view('signup'), methods=['GET', 'POST'])
app.add_url_rule(rule='/account/', view_func=AccountHandler.as_view('account'), methods=['GET'])

app.add_url_rule(rule='/import/', view_func=NewImportHandler.as_view('new_import'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<id>/', view_func=ImportDetailsHandler.as_view('import_details'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<id>/confirm/', view_func=ImportConfirmationHandler.as_view('import_conf'), methods=['GET', 'POST'])
app.add_url_rule(rule='/import/<id>/complete/', view_func=ImportCompleteHandler.as_view('import_complete'), methods=['GET'])

app.add_url_rule(rule='/learn/', view_func=LearningHandler.as_view('learning'), methods=['GET'])
app.add_url_rule(rule='/view/<id>/', view_func=ViewItemHandler.as_view('view'), methods=['GET'])
app.add_url_rule(rule='/compare/<ids>/', view_func=CompareItemsHandler.as_view('compare'), methods=['GET'])

# Define static routes 
# --------------------------------------------------
@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/ads.txt')
def serve_static_files():
    return send_from_directory(app.static_folder, request.path[1:])
