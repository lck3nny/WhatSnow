import pytz
import logging
from datetime import datetime
from flask import render_template, redirect, flash
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
import application.models.skiboard as SkiBoard

__author__ = 'liamkenny'

item_names = ['asym']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   I T E M                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewItemHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, id):
        skiboard, collections = SkiBoard.get_item_by_id(id)
        if not skiboard:
            logging.error("Could not collect SkiBoard: {}".format(id))
            flash('We could not find a ski or board with that ID. Please try again.')

            return redirect('/')

        if collections:
            skiboard['collections'] = collections

        logging.info("Collecting SkiBoard Data:\n{}".format(skiboard))
        return render_template('views/view.html', page_name='view', skiboard=skiboard)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M P A R E   I T E M              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CompareItemsHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, ids):

        if not ids:
            return False

        msg = "Collecting SkiBoard Data:"
        # Collect each item to be compared
        items = []
        for id in ids:
            item, collections = skiboard.get_item_by_id(id)

            if not item:
                flash('We had trouble finding one or more of your comparisons.')
            else:
                item = item.to_dict()
                if collections:
                    item['collections'] = collections

                items.append(item)

                msg += '\n{}'.format(item)
    
        logging.info(msg)
        if not items:
            return redirect('/')
        
        return render_template('core/index.html', page_name='index', skiboards=items)