import json
import pytz
import logging
from datetime import datetime
from difflib import SequenceMatcher

# Infrastructure Imports
# --------------------------------------------------
from flask import render_template, redirect, flash, request
from flask.views import MethodView
from firebase_admin import firestore 

# Model Imports
# --------------------------------------------------
import application.models.skiboard as SkiBoard

__author__ = 'liamkenny'



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# N E W   I M P O R T                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NewImportHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r):
        #return redirect('/')
        return render_template('imports/import.html', page_name='imports')

    # -------------------------------------- P O S T
    def post(r):
        category = request.form.get('category')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')

        # Check if ski / board already exists
        is_duplicate, duplicate = SkiBoard.is_duplicate(category, brand, model, year)
        if is_duplicate:
            link = '/view/{}'.format(duplicate.id)
            link = '/'
            flash('Looks like we already have a listing for this item. Check it out <a href="{}" class="alert-link">here</a>'.format(link))
            return redirect('/import')
        
        # Save ski / board to database 
        try:
            skiboard = SkiBoard.create(brand, model, year, category)
            logging.info("New {} created: \n{}\n".format(category.capitalize(), skiboard))  
            if not skiboard:
                logging.error("Could not create new {}:\n{}".format(category, e))
                flash("We had a problem creating your new {}. Please try again.".format(category))
                return False
        except Exception as e:
            logging.error("Could not create new {}:\n{}".format(category, e))
            flash("We had a problem creating your new {}. Please try again.".format(category))
            return False

        
        return redirect('/import/{}/'.format(skiboard.id))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   D E T A I L S          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportDetailsHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        skiboard = SkiBoard.get_item_by_id(id)
        if not skiboard:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        
        return render_template('imports/import_details.html', page_name='import_details', id=id, skiboard=skiboard, profiles=SkiBoard.profile_categorys)

    # -------------------------------------- P O S T
    def post(r, id):
        skiboard = SkiBoard.get_item_by_id(id)[0]
        raw_input = request.form['data_table']

        # Prevent incomplete submission
        if not skiboard or not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import")
        elif not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import/{}/".format(id))
        
        #skiboard = skiboard.to_dict()
        logging.info("SkiBoard: {}".format(skiboard))
        logging.info("Size Chart Submitted for skiboard:{}\n{}".format(id, raw_input))
        params, units, sizes = SkiBoard.extract_params_from_text(raw_input)
        logging.info("Extracted params: {}\n\nExtracted units: {}".format(params, units))

        # Normalise params
        formatted_params, formatted_units = SkiBoard.format_params(params, units)
        skiboard['params'] = formatted_params
        logging.info("Param formatting complete:\n{}".format(skiboard))

        profiles = SkiBoard.profile_types

        return render_template('imports/import_confirmation.html', page_name='import_conf', id=id, skiboard=skiboard, profiles=profiles)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O N F                H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportConfirmationHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        # Should not arrive here
        return redirect('/import')

    # -------------------------------------- P O S T
    def post(r, id):
        skiboard, collections = SkiBoard.get_item_by_id(id)
        general_info = {
            'category': request.form.get('category'),
            'profile': request.form.get('profile'),
            'asym': request.form.get('asym'),
            'flex': request.form.get('flex')
        }
        logging.info("General Info:\n{}".format(general_info))

        # Retreive hidden params from form
        params = {}
        for key in SkiBoard.param_names:
            param_list = request.form.get(key+'-hidden-vals')
            if param_list:
                params[key] = param_list.split(',')

        logging.info("Params:\n{}".format(params))
    
        # Update general info for SkiBoard
        logging.info("Import Confirmation...\Category: {}\nProfile: {}\nAsym: {}\nFlex: {}\nParams:\n{}".format(general_info['category'], general_info['profile'], general_info['asym'], general_info['flex'], params))
        logging.info("SkiBoard: {}".format(skiboard))
        success = SkiBoard.update_info(id, general_info, params)
        if not success:
            flash("We were unable to update this {}".format(general_info['category'].title))
            return False
 
        return render_template('imports/import_complete.html', page_name='import_complete', skiboard=skiboard, item_id=id)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O M P L E T E        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportCompleteHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        skiboard = SkiBoard.get_item_by_id(id)
        if not skiboard:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        return render_template('imports/import_complete.html', page_name='import_complete', skiboard=skiboard)
