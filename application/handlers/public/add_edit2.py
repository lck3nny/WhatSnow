import logging

# Infrastructure Imports
# --------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
#from application.models.skiboard import SkiBoard

from application.models.skiboard2 import SkiBoard
from application.models.user import User

__author__ = 'liamkenny'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# N E W   I M P O R T                            H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NewImportHandler2(MethodView):
    # ---------------------------------------- G E T
    def get(r):
        if not 'user' in session:
            logging.info("No user in session")
            return redirect('/login')
        
        brands = SkiBoard.get_brands()

        
        '''
        if not User.is_admin(session['user']['id']):
            logging.info("User not admin. Redirecting. {}".format(session['user']))
            return redirect('/comingsoon')
        '''
        

        return render_template('add-edit/import2.html', page_name='imports', brands=brands.keys())
