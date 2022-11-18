from flask import render_template, redirect, session, flash
from flask.views import MethodView

__author__ = 'liamkenny'

class LoginHandler(MethodView):
    def get(request):
        if 'user' in session:
            return redirect('/account')
        return render_template('login.html', session=session, page_name='login')

    def post(request):
        user = {
            'first_name': 'Liam',
            'last_name': 'Kenny',
            'email': 'lck3nny.dev@gmail.com',
            'role': 'admin'
        }
        flash('You have been successfully logged in as {} {}'.format(user['first_name'], user['last_name']))
        session.permanent = True
        session['user'] = user
        return redirect('/account')

class LogoutHandler(MethodView):
    def get(request):
        if 'user' in session:
            flash('You have been successfully logged out.', 'info')

        session.pop('user', None)
        return redirect('/')


class SignupHandler(MethodView):
    def get(request):
        return render_template('signup.html', session=session, page_name='signup')

class AccountHandler(MethodView):
    def get(request):
        if 'user' in session:
            return render_template('account.html', session=session, page_name='account')
        else:
            return redirect('/login')


