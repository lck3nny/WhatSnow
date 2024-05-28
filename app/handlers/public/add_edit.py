import logging

# Infrastructure Imports
# ------------------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView

# Model Imports
# ------------------------------------------------------------
from app.models.skiboard import SkiBoard
from app.models.user import User

__author__ = 'liamkenny'

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
            if not User.is_admin(session['user']['id']):
                logging.info("User not admin. Redirecting. {}".format(session['user']))
                return redirect('/comingsoon')
            

        active_import = {}
        if 'import' in session and 'skiboard' in session['import']:
            skiboard , collections= SkiBoard.get_item_by_slug(session['import']['skiboard'])[0]
            if skiboard:
                logging.info("Active import found in session: {}".format(skiboard))
                active_import['id'] = session['import']['skiboard']
                active_import['name'] = skiboard['name']
            else:
                session.pop('import', None)

        return render_template('add-edit/import.html', page_name='imports', active_import=active_import, comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(r):
        category = request.form.get('category').title()
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = int(request.form.get('year'))

        # Upper case first letter of each word
        # Leave all other letters as unchanged
        brand = SkiBoard.normaise_brand_model(brand)
        model = SkiBoard.normaise_brand_model(model)

        # Check if ski / board already exists
        is_duplicate, duplicate = SkiBoard.is_duplicate(category, brand, model, year)
        if is_duplicate:
            link = '/view/{}'.format(duplicate.id)
            link = '/'
            flash('It looks lke you were trying to add a {} we already have. Check it out here!'.format(category))
            return redirect('/view/{}'.format(duplicate.to_dict()['slug']))
        
        author = None
        if 'user' in session and 'id' in session['user']:
            author = session['user']['id']
        else:
            logging.warning("User ID missing from session")
        
        # Save ski / board to database 
        success, skiboard = SkiBoard.create(brand, model, year, category, author)
        logging.info("New {} created: \n{}\n".format(category.title(), skiboard))  
        if not success:
            logging.error("Could not create new {}".format(category))
            flash("We had a problem creating your new {}. Please try again.".format(category))
            return redirect('/import')
        
        session['import'] = {'skiboard': skiboard['slug']}

        return redirect('/import/{}/'.format(skiboard['slug']))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   D E T A I L S                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportDetailsHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(r, slug):
        if not 'user' in session:
            logging.info("No user in session")
            return redirect('/comingsoon')
        else:
            if not User.is_admin(session['user']['id']):
                logging.info("User not admin. Redirecting. {}".format(session['user']))
                return redirect('/comingsoon')

        skiboard = SkiBoard.get(slug=slug)
        if not skiboard:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')

        description = SkiBoard.describe()
        return render_template('add-edit/import_details.html', page_name='import_details', skiboard=skiboard, profiles=description['profile_types'], comparisons=SkiBoard.calc_comparisons())

    # ------------------------------------------------ P O S T
    def post(r, slug):
        try:
            skiboard , collections= SkiBoard.get_item_by_slug(slug)[0]
        except:
            logging.error("No SkiBoard found with slug: {}".format(slug))
            return redirect('/import')
        
        raw_input = request.form['data-table']
        general_info = {
            'asym': request.form.get('asym'),
            'flex': request.form.get('flex'),
            'profile': request.form.get('profile')
        }

        # Prevent incomplete submission
        if not skiboard or not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import")
        elif not raw_input:
            flash("We could not process your import. Please try again.")
            return redirect("/import/{}/".format(slug))
        
        #skiboard = skiboard.to_dict()
        logging.info("SkiBoard: {}".format(skiboard))
        logging.info("Size Chart Submitted for skiboard:{}\n{}".format(slug, raw_input))
        params, units, sizes = SkiBoard.extract_params_from_text(raw_input)
        logging.info("Extracted params: {}\n\nExtracted units: {}".format(params, units))

        # Normalise params
        formatted_params, formatted_units = SkiBoard.format_params(params, units)
        skiboard['params'] = formatted_params
        logging.info("Param formatting complete:\n{}".format(skiboard))

        description = SkiBoard.describe()
        session['import'] = {'skiboard': skiboard['slug']}


        return render_template('add-edit/import_confirmation.html', page_name='import_conf', slug=slug, skiboard=skiboard, profiles=description['profile_types'], general_info=general_info, comparisons=SkiBoard.calc_comparisons())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O N F                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportConfirmationHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(r, slug):
        # Should not arrive here
        return redirect('/import')

    # ------------------------------------------------ P O S T
    def post(r, slug):
        skiboard, collections = SkiBoard.get_item_by_slug(slug)
        general_info = {
            'category': request.form.get('category').title(),
            'profile': request.form.get('profile').title(),
            'asym': request.form.get('asym') == 'True', 
            'flex': request.form.get('flex')
        }
        logging.info("General Info:\n{}".format(general_info))

        # Retreive hidden params from form
        params = {}
        description = SkiBoard.describe()
        for key in description['param_names']:
            param_list = request.form.get(key+'-hidden-vals')
            if param_list:
                params[key] = param_list.split(',')

        logging.info("Params:\n{}".format(params))
    
        # Update general info for SkiBoard
        logging.info("Import Confirmation...\Category: {}\nProfile: {}\nAsym: {}\nFlex: {}\nParams:\n{}".format(general_info['category'], general_info['profile'], general_info['asym'], general_info['flex'], params))
        logging.info("SkiBoard: {}".format(skiboard))
        success, es_resp, new_skiboard = SkiBoard.update_info(skiboard['id'], general_info, params)
        if not success:
            flash("We were unable to update this {}".format(general_info['category'].title))
            return redirect('/import/{}'.format(skiboard.slug))
        
        if not es_resp:
            flash("We could not add this {} to our ElasticSearch database.")
            logging.error("ElasticSearch upload error:\n{}".format(es_resp))
        
        logging.info("New Skiboard:\n{}".format(new_skiboard))
        logging.info("ElasticSearch Response:\n{}".format(es_resp))

        if 'import' in session:
            session.pop('import', None)
 
        return render_template('add-edit/import_complete.html', page_name='import_complete', skiboard=skiboard, comparisons=SkiBoard.calc_comparisons())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# I M P O R T   C O M P L E T E                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ImportCompleteHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(r, slug):
        if not 'user' in session:
            logging.info("No user in session")
            return redirect('/comingsoon')
        else:
            if not User.is_admin(session['user']['id']):
                logging.info("User not admin. Redirecting. {}".format(session['user']))
                return redirect('/comingsoon')

        if 'import' in session:
            session.pop('import', None)

        skiboard , collections= SkiBoard.get_item_by_slug(slug)
        if not skiboard:
            flash('There was a problem with your connection. Please restart the import process.')
            return redirect('/import')
        
        return render_template('add-edit/import_complete.html', page_name='import_complete', skiboard=skiboard, comparisons=SkiBoard.calc_comparisons())


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
            return redirect('/view/slug/')
                
        return render_template('add-edit/edit_skiboard.html', page_name='import_complete', skiboard=skiboard, comparisons=SkiBoard.calc_comparisons())
    
    def post(r, slug):
        logging.info(f"Submitting new edit for skiboard {slug}")

        skiboard = SkiBoard.get(slug=slug)
        if not skiboard:
            flash('There was a problem with your request. Please try again later!')
            return redirect('/view/slug/')
        

        #raw_input = request.form['raw-data']
        update_params = {
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

        logging.info("Updating params one at a time")
        for p in update_params:
            try:
                setattr(skiboard, p, update_params[p])
            except Exception as e:
                logging.error(f"Untable to update {p} in SkiBoard: {slug}... {e}")

        logging.info("Saving new params to skiboard")
        try:
            skiboard.save()
        except Exception as e:
            logging.error(f"Could not save SkiBoard: {slug}... {e}")
            flash('There was a problem with your request. Please try again later!')
            return redirect('/view/slug/')
        
        flash('Ski / Snowboard successfully updated.')
        return redirect(f'/view/{slug}/')

