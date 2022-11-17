from flask import render_template, redirect
from flask.views import MethodView

__author__ = 'liamkenny'

class LoginHandler(MethodView):
    def get(request):
        return render_template('login.html')

    def post(request):
        return redirect('/account')

class SignupHandler(MethodView):
    def get(request):
        return render_template('signup.html')

class AccountHandler(MethodView):
    def get(request):
        user = {
            'first_name': 'Liam',
            'last_name': 'Kenny',
            'email': 'lck3nny.dev@gmail.com',
            'role': 'admin'
        }
        return render_template('account.html', user=user)

