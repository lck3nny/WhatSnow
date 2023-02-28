import json
from datetime import datetime
from flask import render_template, redirect, session, flash, request
from flask.views import MethodView
from difflib import SequenceMatcher


__author__ = 'liamkenny'


unit_names = {
    'size':         ['size', 'length'],
    'nose_width':   ['nose width', 'tip width'],
    'waist_width':  ['waist width'],
    'tail_width':   ['tail width'],
    'sidecut':      ['sidecut', 'sidecut radius' 'turning radius'],
    'bend':         ['bend', 'profile'],
    'flex':         ['flex', 'stiffness']
}

# --------------------------------------------------
# Is Duplicate                       F U N C T I O N
# --------------------------------------------------
def is_duplicate(type, brand, model, year):
    return False

# --------------------------------------------------
# Get Stats By ID                    F U N C T I O N
# --------------------------------------------------
def get_item_by_id(id):
    item = {
            'id': id,
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022'
        }
    return item

# --------------------------------------------------
# Get Stats For Item                 F U N C T I O N
# --------------------------------------------------
def get_stats_for_item(item):
    item = {
            'id': id,
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022',
            'nose_width': 300,
            'waist_width': 255,
            'tail_width': 292,
            'sidecut': 7.2
        }
    return item

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
    return_params = {
        'size': None,
        'nose_width': None,
        'waist_width': None,
        'tail_width': None,
        'sidecut': None,
        'bend': None,
        'flex': None
    }

    best_matches = {
        'size': [],
        'nose_width': [],
        'waist_width': [],
        'tail_width': [],
        'sidecut': [],
        'bend': [],
        'flex': []
    }

    # Generate list of best matches for each valid param name
    for param in params:
        if param:
            key, match_score = find_best_param_match(param)
            best_matches[key].append(match_score)


    # Find the highest scoring match for each valid param name
    for param in best_matches:
        best_match = ""
        best_score = 0
        for match in best_matches[param]:
            for name in match:
                if match[name] > best_score:
                    best_score = match[name]
                    best_match = name

        return_params[param] = best_match
        
    # Return best matching input param names for each valid param name
    return return_params

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
        if is_duplicate(import_type, brand, model, year):
            flash('Looks like we already have a listing for this item. Check it out <a href="/" class="alert-link">here</a>')
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
        new_item = get_item_by_id(id)
        if not new_item:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')
        
        item = {
            'type': 'Snowboard',
            'brand': 'Burton',
            'model': 'Custom',
            'year': '2022'
        }
        return render_template('imports/import_details.html', page_name='import_details', import_item=item)

    # -------------------------------------- P O S T
    def post(r, id):
        from ... import app
        raw_data = request.form['data_table']
        item = get_item_by_id(id)

        # Logging imported data
        msg = "\nSize Chart Submitted: \n{}".format(raw_data)

        app.logger.info("Submitted Data:")
        app.logger.info(msg)

        f = open("logs.txt", "a")
        f.write("{}\nLOGGING... {}\n\n".format(datetime.now(), msg))
        f.close()

        # Extract Data from raw table
        sizes = 0
        params = {}
        param_units = {}
        f = open("logs.txt", "a")
        f.write("{}\nEXTRACTING...".format(datetime.now()))
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

        
        
        return render_template('imports/import_confirmation.html', page_name='import_conf', data=data, options=unit_names, sizes=sizes)

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
        new_item = get_item_by_id(id)
        if not new_item:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        item = get_stats_for_item(item)

        return render_template('imports/import_complete.html', page_name='import_complete', item=item)

