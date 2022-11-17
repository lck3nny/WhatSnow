from flask import Flask, request, send_from_directory
from .handlers.public.home import HomePageHandler

__author__ = 'liamkenny'

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

# Define public routes
# --------------------------------------------------
app.add_url_rule(rule='/', view_func=HomePageHandler.as_view('home'), methods=['GET'])

# Define static routes
# --------------------------------------------------
@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/ads.txt')
def serve_static_files():
    return send_from_directory(app.static_folder, request.path[1:])
