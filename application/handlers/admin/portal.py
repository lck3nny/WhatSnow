import pytz
import logging
from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
import application.models.user as User

__author__ = 'liamkenny'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# P O R T A L                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminPortalHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        if 'user' not in session:
            return redirect('/login')

        logging.info("Checking user permissions: {}".format(session['user']))
        if not (User.is_admin(session['user']['id'])):
            return redirect('/')

        return render_template('admin/portal.html', session=session, page_name='admin_portal')

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   U S E R S                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminViewUsersHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        
        if 'user' not in session:
            return redirect('/')

        if not (User.is_admin(session['user']['id'])):
            return redirect('/')

        return render_template('admin/view_users.html', session=session, page_name='admin_view_users')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   S I N G L E   U S E R      H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminViewSingleUsersHandler(MethodView):
    # ---------------------------------------- G E T    
    def get(self):
        if 'user' not in session:
            return redirect('/')

        if not (User.is_admin(session['user']['id'])):
            return redirect('/')

        return render_template('admin/view_single_user.html', session=session, page_name='admin_veiew_single_user')