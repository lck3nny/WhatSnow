from flask import render_template
from flask.views import MethodView

__author__ = 'liamkenny'

class HomePageHandler(MethodView):
    def get(request):
        return render_template('index.html')