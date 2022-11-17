from flask import Flask, request, send_from_directory
from .handlers.public.home import HomePageHandler
from .handlers.public.accounts import LoginHandler, SignupHandler, AccountHandler
from .handlers.public.imports import NewImportHandler
from .handlers.public.learning import LearningHandler

__author__ = 'liamkenny'

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

# Define public routes
# --------------------------------------------------
app.add_url_rule(rule='/', view_func=HomePageHandler.as_view('home'), methods=['GET'])
app.add_url_rule(rule='/login/', view_func=LoginHandler.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule(rule='/signup/', view_func=SignupHandler.as_view('signup'), methods=['GET', 'POST'])
app.add_url_rule(rule='/account/', view_func=AccountHandler.as_view('account'), methods=['GET'])
app.add_url_rule(rule='/import/', view_func=NewImportHandler.as_view('new_import'), methods=['GET'])
app.add_url_rule(rule='/learn/', view_func=LearningHandler.as_view('learning'), methods=['GET'])

# Define static routes 
# --------------------------------------------------
@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/ads.txt')
def serve_static_files():
    return send_from_directory(app.static_folder, request.path[1:])
