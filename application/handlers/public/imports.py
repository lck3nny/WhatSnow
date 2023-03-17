import json
import pytz
import logging
from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
from difflib import SequenceMatcher

# Model Imports
# --------------------------------------------------
import application.models.skiboard as skiboard

__author__ = 'liamkenny'

unit_names = {
    'size':         ['size', 'length'],
    'nose_width':   ['nose width', 'tip width'],
    'waist_width':  ['waist width'],
    'tail_width':   ['tail width'],
    'sidecut':      ['sidecut', 'sidecut radius' 'turning radius'],
    'setback':      ['stance setback'],
    'stance range': ['stance range'],
    'profile':      ['bend', 'profile'],
    'flex':         ['flex', 'stiffness'],
    'asym':         False
}


# --------------------------------------------------
# Find Best Param Name Match         F U N C T I O N
# --------------------------------------------------
def find_best_param_match(param):
    match_scores = {
        'size': 0,
        'nose_width': 0,
        'waist_width': 0,
        'tail_width': 0,
        'sidecut': 0,
        'bend': 0,
        'flex': 0
    }

    # Compare each possible param with given name
    # Store highest similarity score for any unit name
    for key in unit_names:
        scores = []
        for name in unit_names[key]:
            scores.append(SequenceMatcher(None, name, param).ratio())

        match_scores[key] = max(scores)

    # Find the param with the highest comparison score
    max_score = 0
    best_match = ''
    for key in match_scores:
        if match_scores[key] > max_score:
            max_score = match_scores[key]
            best_match = key
        
    if max_score == 0:
        return None

    return key, {param: max_score}

# --------------------------------------------------
# Match Import Params                F U N C T I O N
# --------------------------------------------------
def match_params(params, units):

    best_matches = {
        'size': {},
        'nose_width': {},
        'waist_width': {},
        'tail_width': {},
        'sidecut': {},
        'bend': {},
        'flex': {}
    }

    # Generate list of best matches for each valid param name
    for param in params:
        if param:
            key, match_score = find_best_param_match(param)
            best_matches[key].append(match_score)

        
    # Return best matching input param names for each valid param name
    return best_matches

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

        is_duplicate = skiboard.is_duplicate(import_type, brand, model, year)
        if is_duplicate[0]:
            link = '/view/{}'.format(is_duplicate[1].id)
            link = '/'
            flash('Looks like we already have a listing for this item. Check it out <a href="{}" class="alert-link">here</a>'.format(link))
            return redirect('/import')

        # Save ski / board to database
        id = 123
        return redirect('/import/{}/'.format(id))

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
        from ... import app
        raw_data = request.form['data_table']
        item = skiboard.get_item_by_id(id)
        logging.info("Size Chart Submitted: \n{}".format(raw_data))

        # Extract Data from raw table
        sizes = 0
        params = {}
        param_units = {}
        f = open("logs.txt", "a")
        f.write("{}\nEXTRACTING...".format(datetime.now(pytz.timezone('Canada/Pacific'))))
        for line in raw_data.split('\n'):
            f.write("\n{}".format(line))
            split_line = line.split(" ")
            
            line_name = " ".join(split_line[:-1])
            f.write("\nName: {}".format(line_name))

            units = str(line)[line.find('(') +1:line.find(')')]
            f.write("\nUnits: {}".format(units))
            
            values = split_line[-1].split('\t')[1:]
            for x, v in enumerate(values):
                values[x] = v.replace('\r', '')
            f.write("\nValues: {}".format(values))

            #params.append({'key': line_name, 'unit': units, 'values': values})
            params[line_name.replace(' ', '_')] = values
            param_units[line_name.replace(' ', '_')] = values

            sizes += 1
        
        f.write('\nUnformatted params:\n{}'.format(json.dumps(params)))
        formatted_params = match_params(params, units)
        f.write('\n\nFormatted params:\n{}\n\n'.format(json.dumps(formatted_params)))
        f.close()

        # Format completed data object
        data = {
            'type': item['type'],
            'brand_name': item['brand'],
            'model_name': item['model'],
            'year': item['year'],
            'params': []
        }

        # Populate data object with matched params
        for param in formatted_params:
            new_param = {
                'name': None,
                'matched': None,
                'val_name': None,
                'vals': []
            }

            data['params'].append(new_param)

        unit_options = list(unit_names.keys())
        
        return render_template('imports/import_confirmation.html', page_name='import_conf', data=data, options=unit_options, sizes=sizes)

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

