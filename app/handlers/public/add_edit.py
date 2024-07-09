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
            skiboard = SkiBoard.get(slug=new_skiboard.slug)

            if not success:
                flash("Something went wrong with your import, please try again")
                return redirect('/import/')
        except Exception as e:
            logging.error(f"Unable to save new skiboard to DB: {e}")


        # Extract RAW Table Data from String
        try:
            extracted_params = Size.extract_raw_size_data(request.form.get('raw_data'))
            logging.info(f"Extracted Params: {extracted_params}")

            success, msg = Size.save_batch_data(skiboard, extracted_params)
            if not success:
                logging.error(f"Unable to save sizes using raw data: {msg}")
        except Exception as e:
            logging.error(f"Could not successfully add size data using raw input: {e}")
    

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
            # Extract RAW Table Data from String
            try:
                extracted_params = Size.extract_raw_size_data(request.form.get('raw_data'))
                logging.info(f"Extracted Params: {extracted_params}")

                success, msg = Size.save_batch_data(skiboard, extracted_params)
                if not success:
                    logging.error(f"Unable to save sizes using raw data: {msg}")
            except Exception as e:
                logging.error(f"Could not successfully add size data using raw input: {e}")
                
        
        flash('Ski / Snowboard successfully updated.')
        return redirect(f'/view/{slug}/')

