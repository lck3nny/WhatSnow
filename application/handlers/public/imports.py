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
import application.models.skiboard as skiboard

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
        import_type = request.form.get('type')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')

        is_duplicate, duplicate = skiboard.is_duplicate(import_type, brand, model, year)
        if is_duplicate:
            link = '/view/{}'.format(duplicate.id)
            link = '/'
            flash('Looks like we already have a listing for this item. Check it out <a href="{}" class="alert-link">here</a>'.format(link))
            return redirect('/import')

        # Save ski / board to database        
        try:
            db = firestore.client()
            create_time, new_skiboard = db.collection('SkiBoards').add({
                'brand': brand,
                'model': model,
                'year': year,
                'type': import_type,
                'created': datetime.now(pytz.timezone('Canada/Pacific'))
            })
            logging.info("New {} created: \n{}\n".format(import_type.capitalize(), new_skiboard))     
        except Exception as e:
            logging.error("Could not create new {}:\n{}".format(import_type, e))

        
        return redirect('/import/{}/'.format(new_skiboard.id))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   D E T A I L S          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportDetailsHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        new_item = skiboard.get_item_by_id(id)
        if not new_item:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        
        return render_template('imports/import_details.html', page_name='import_details', skiboard=new_item)

    # -------------------------------------- P O S T
    def post(r, id):
        item = skiboard.get_item_by_id(id)
        raw_input = request.form['data_table']

        # Prevent incomplete submission
        if not item or not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import")
        elif not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import/{}/".format(id))

        logging.info("Size Chart Submitted for skiboard:{}\n{}".format(id, raw_input))
        params, units, sizes = skiboard.extract_params_from_text(raw_input)
        logging.info("Extracted params: {}\n\nExtracted units: {}".format(params, units))

        # Normalise params
        formatted_params = skiboard.format_params(params, units)
        unit_options = list(skiboard.unit_names.keys())

        # Update firebase doc
        
                
        return render_template('imports/import_confirmation.html', page_name='import_conf', skiboard=item)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O N F                H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportConfirmationHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        return redirect('/import')

    # -------------------------------------- P O S T
    def post(r, id):
        import_type = request.form.get('type')
        return render_template('imports/import_complete.html', page_name='import_complete', item_type=import_type, item_id=id)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O M P L E T E        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportCompleteHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r, id):
        new_item = skiboard.get_item_by_id(id)
        if not new_item:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        return render_template('imports/import_complete.html', page_name='import_complete', skiboard=new_item)

