from flask import render_template, redirect
from flask.views import MethodView

__author__ = 'liamkenny'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# L E A R N I N G                      H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class LearningHandler(MethodView):
    # ---------------------------------------- G E T
    def get(request):
        return redirect('/')
