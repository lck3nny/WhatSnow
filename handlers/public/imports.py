from flask import render_template, redirect
from flask.views import MethodView

__author__ = 'liamkenny'

class NewImportHandler(MethodView):
    def get(request):
        return redirect('/')
