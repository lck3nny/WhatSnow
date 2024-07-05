import logging, re

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.models.skiboard import SkiBoard
from app.models.user import User
from app.models.size import Size

# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView

__author__ = 'liamkenny'

default_params = {
    'size': ['size', 'length'],
    'nose width': ['nose width', 'tip width'],
    'waist width': ['waist width'],
    'tail width': ['tail width'],
    'sidecut': ['sidecut radius', 'turning radius', 'radius', 'sidecut'],
    'setback': ['stance setback', 'setback'],
    'effective edge': ['effective edge', 'running length']
}

# I M P O R T S
# E X T R A C T   R A W   D A T A              F U N C T I O N   
# ------------------------------------------------------------
# Extraction of data 
# from string format to a tabular structure
# ------------------------------------------------------------
def extract_raw_data(table):
    values = {
        'size': '',
        'nose width': '',
        'waist width': '',
        'tail width': '',
        'sidecut': '',
        'setback': '',
        'effective edge': ''
    }
    
    # Remove units from headings
    while re.search(r'\(([a-zA-Z]+)\)', table) != None:
        match = re.search(r'\(([a-zA-Z]+)\)', table)
        substr = table[match.start():match.end()]
        table = table.replace(substr, '')
    '''    
    while ')' in table:
        table = table[:table.find('(')] + table[table.find(')') + 1:]
    '''    
        
    breakpoints = []
    
    # Find location of headings in table
    for i in default_params:
        # Check each param alias
        for j in default_params[i]:
            if j in table:
                breakpoints.append(table.find(j))
                break
        
        values[i] = []
        
    # Extract table data into rows
    rows = []
    breakpoints.sort()
    for i, b in enumerate(breakpoints):
        if i > 0:
            rows.append(table[breakpoints[i-1]:b])
            print(f"Row: {table[breakpoints[i-1]:b]}")
        if i == len(breakpoints) -1:
            rows.append(table[b:])
    
    
    # Remove lables from rows
    for row in rows:
        for i in default_params:
            for j in default_params[i]:
                if j in row:
                    values[i] = row.replace(j, '')
                    break
                    
    
    # Format table rows as lists
    for val in values:
        try:
            # \u0020\u200b\u002f\u0020
            # \u0020\u002f\u0020
            values[val] = values[val].strip()
            values[val] = values[val].replace('\u0020\u002f\u0020', '/')
            values[val] = values[val].replace('\u0020\u200b\u002f\u0020', '/')
            values[val] = values[val].replace('\u0020\u200b\u200b\u002f\u0020', '/')
            values[val] = values[val].split() 
            
        except Exception as e:
            x = e
            
    
    # Truncate long rows to the correct size
    num_sizes = len(values['size'])
    for val in values:
        # Sidecuts can have more than one radius
        if val != "sidecut":
            values[val] = values[val][:num_sizes]

        # Remove rogue characters from row values
        if len(values[val]) > 0 and type(values[val][0]) == str:
            for x, v in enumerate(values[val]):
                values[val][x] = values[val][x].replace('\u200b', '')
        
        
        # Fill empty or missing data with null values
        for x in range(num_sizes - len(values[val])):
            values[val].append(0)
            

    return values


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# N E W   I M P O R T                            H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NewImportHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(r):
        if not 'user' in session:
            logging.info("No user in session")
            return redirect('/comingsoon')
        else:
            user = User.get(id=session['user']['id'])
            if not user.is_admin:
                logging.info("User not admin. Redirecting. {}".format(session['user']))
                return redirect('/comingsoon')

        return render_template('add-edit/import.html', page_name='imports', comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(r):
        if not 'user' in session:
            logging.info("No user in session")
            return redirect('/comingsoon')
        
        basic_info = {
            'category': request.form.get('category'),
            'brand': request.form.get('brand'),
            'model': request.form.get('model'),
            'year': request.form.get('year')
        }

        # TODO...
        # CHECK THAT ATTEMPTED IMPORT IS NOT A DUPLICATE

        return render_template('add-edit/import_details.html', page_name='import_details', basic_info=basic_info, comparisons=SkiBoard.calc_comparisons())



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M P L E T E   I M P O R T                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CompleteImportHandler(MethodView):
    # ------------------------------------------------ P O S T
    def post(r):

        logging.info("Final Import Stage")
        logging.info(f"Brand: {request.form.get('brand')} / Model: {request.form.get('model')} / Year: {request.form.get('year')} / Category: {request.form.get('category')}")

        try:
            new_skiboard = SkiBoard(
                skiboard_id=-1,
                brand=request.form.get('brand'),
                model=request.form.get('model'),
                year=request.form.get('year'),
                category=request.form.get('category')
            )
        except Exception as e:
            logging.error(f"Unable to set baseline properties of new skiboard for import: {e}")

        try:
            optional_properties = {
                'description': request.form.get('description'),
                'stiffness': request.form.get('stiffness'),
                'shape': request.form.get('shape'),
                'family': request.form.get('family'),
                'flex_profile': request.form.get('flexprofile'),
                'camber_profile': request.form.get('camberprofile'),
                'camber_details': request.form.get('camberdetails'),
                'core': request.form.get('core'),
                'core_profiling': request.form.get('coreprofiling'),
                'fibreglass': request.form.get('fibreglass'),
                'laminates': request.form.get('laminates'),
                'resin': request.form.get('resin'),
                'base': request.form.get('base'),
                'edges': request.form.get('edges'),
                'edge_tech': request.form.get('edgetech'),
                'topsheet': request.form.get('topsheet'),
                'sidewall': request.form.get('sidewall'),
                'inserts': request.form.get('inserts'),
                'asym': request.form.get('asym'),
                'weight': request.form.get('weight'),
                'womens': request.form.get('womens'),
                'youth': request.form.get('youth')
            }

            for key, val in optional_properties.items():
                if val:
                    logging.info(f"Updating new skiboard with optional paral ({key}): {val}")
                    setattr(new_skiboard, key, val)
        except Exception as e:
            logging.error(f"Unable to extract / set optional properties for new skiboard: {e}")
            
        try:
            logging.info(f"Saving new skiboard: {new_skiboard}")
            success = new_skiboard.save()

            if not success:
                flash("Something went wrong with your import, please try again")
                return redirect('/import/')
        except Exception as e:
            logging.error(f"Unable to save new skiboard to DB: {e}")

        try:
            values = extract_raw_data(request.form.get('raw_data'))
            if values:
                new_skiboard.save_values(values)
            else:
                logging.info("No values provided for import")
        except Exception as e:
            logging.error(f"Failed to extract raw data values: {e}")
        

        return redirect(f'/view/{new_skiboard.slug}/')



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# E D I T    S K I B O A R D                     H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class EditSkiboard(MethodView):
    # -------------------------------------------------- G E T
    def get(r, slug):
        logging.info("EDIT SKIBOARD: {}".format(str(slug)))

        skiboard = SkiBoard.get(slug=slug)
        if not skiboard:
            flash('There was a problem with your request. Please try again later!')
            return redirect(f'/view/{slug}/')
        
        try:
            sizes = Size.get(skiboard.id)
            for x, size in enumerate(sizes):
                sizes[x] = size.__dict__

            logging.info(f"Sizes for {skiboard.name}:\n{sizes}")
        except Exception as e:
            logging.error(f"Could not get sizes for skiboard ({skiboard.name}): \n{e}")
                
        return render_template('add-edit/edit_skiboard.html', page_name='import_complete', skiboard=skiboard, sizes=sizes, comparisons=SkiBoard.calc_comparisons())
    
    # ------------------------------------------------ P O S T
    def post(r, slug):
        logging.info(f"Submitting new edit for skiboard {slug}")

        skiboard = SkiBoard.get(slug=slug)
        if not skiboard:
            flash('There was a problem with your request. Please try again later!')
            return redirect('/view/slug/')
        

        # Collect list of params for general SkiBoard data
        skiboard_update_params = {
            'description': request.form.get('description'),
            'family': request.form.get('family'),
            'stiffness': request.form.get('stiffness'),
            'shape': request.form.get('shape'),
            'flex_profile': request.form.get('flex_profile'),
            'camber_profile': request.form.get('camberprofile'),
            'camber_details': request.form.get('camberdetails'),
            'core': request.form.get('core'),
            'core_profiling': request.form.get('coreprofiling'),
            'fibreglass': request.form.get('fibreglass'),
            'laminates': request.form.get('laminates'),
            'resin': request.form.get('resin'),
            'base': request.form.get('base'),
            'edges': request.form.get('edges'),
            'edge_tech': request.form.get('edge_tech'),            
            'topsheet': request.form.get('topsheet'),
            'sidewall': request.form.get('sidewall'),
            'inserts': request.form.get('inserts'),
            'asym': request.form.get('asym'),
            'weight': request.form.get('weight'),
            'womens': request.form.get('womens'),
            'youth': request.form.get('youth')
        }

        # Apply param updates to local SkiBoard object
        logging.info("Updating params one at a time")
        for p in skiboard_update_params:
            try:
                setattr(skiboard, p, skiboard_update_params[p])
            except Exception as e:
                logging.error(f"Untable to update {p} in SkiBoard: {slug}... {e}")

        # Update DB with new params
        logging.info("Saving new params to skiboard")
        try:
            skiboard.save()
        except Exception as e:
            logging.error(f"Could not save SkiBoard: {slug}... {e}")
            flash('There was a problem with your request. Please try again later!')
            return redirect('/view/slug/')
        

        logging.info(" ------------------------- ")
        logging.info(f"Form Values: {request.form.to_dict()}")
        # Collect list of params for Size data
        num_sizes = request.form.get('num_sizes')
        if num_sizes:
            for x in range(1, int(num_sizes)+1):
                try:
                    single_size = Size(
                        skiboard_id = skiboard.id,
                        size = request.form.get(f'size_{x}'),
                        nose_width = request.form.get(f'nose_width_{x}'),
                        waist_width = request.form.get(f'waist_width_{x}'),
                        tail_width = request.form.get(f'tail_width_{x}'),
                        sidecut = request.form.get(f'sidecut_{x}'),
                        setback = request.form.get(f'setback_{x}'),
                        effective_edge = request.form.get(f'effective_edge_{x}')
                    )
                    logging.info(f"Extracted Single Size: {single_size.__dict__}")

                    '''
                    if skiboard['category'].lower() == 'ski':
                        single_size['factory_mounting_point'] = request.form.get(f'factory_mounting_point_{x}')
                        single_size['freestyle_mounting_point'] = request.form.get(f'freestyle_mounting_point_{x}')
                    '''
                    # Save each size provided in
                    success = single_size.save()
                    if not success:
                        logging.warning(f"Unable to save size: x = {x}")
            

                except Exception as e:
                    logging.info(f"Breaking size loop at x = {x} /// {e}")
                    break            
        elif request.form.get('raw_data'):
            logging.info("Must have a raw data input")
        
        flash('Ski / Snowboard successfully updated.')
        return redirect(f'/view/{slug}/')

