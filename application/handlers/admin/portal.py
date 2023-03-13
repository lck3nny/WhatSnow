from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
import pyrebase
import json

__author__ = 'liamkenny'

# --------------------------------------------------
# Is Admin User                      F U N C T I O N
# --------------------------------------------------
def check_admin_user(user):
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# P O R T A L                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Í
class AdminPortalHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        user = session['user']
        if not user:
            return redirect('/')

        if not (check_admin_user(user)):
            return redirect('/')

        return render_template('admin/portal.html', session=session, page_name='admin_portal')

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   U S E R S                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Í
class AdminViewUsersHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        user = session['user']
        if not user:
            return redirect('/')

        if not (check_admin_user(user)):
            return redirect('/')

        return render_template('admin/view_users.html', session=session, page_name='admin_view_users')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   S I N G L E   U S E R      H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Í
class AdminViewSingleUsersHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        user = session['user']
        if not user:
            return redirect('/')

        if not (check_admin_user(user)):
            return redirect('/')

        return render_template('admin/view_single_user.html', session=session, page_name='admin_veiew_single_user')