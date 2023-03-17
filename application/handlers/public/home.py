import logging
from flask import render_template
from flask.views import MethodView

__author__ = 'liamkenny'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# H O M E                              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class HomePageHandler(MethodView):
    # ---------------------------------------- G E T
    def get(request):
        return render_template('core/index.html', page_name='index')
    