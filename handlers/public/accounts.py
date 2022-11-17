from flask import render_template
from flask.views import MethodView

__author__ = 'liamkenny'

class LoginHandler(MethodView):
    def get(request):
        return render_template('login.html')

class SignupHandler(MethodView):
    def get(request):
        return render_template('signup.html')

class AccountHandler(MethodView):
    def get(request):
        return render_template('account.html')