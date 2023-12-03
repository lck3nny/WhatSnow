import logging
from flask import render_template, redirect, flash, session, request
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
from application.models.skiboard import SkiBoard
from application.models.user import User

__author__ = 'liamkenny'

item_names = ['asym']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   I T E M                              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, slug):
        skiboard, collections = SkiBoard.get_item_by_slug(slug)
        if not skiboard:
            logging.error("Could not collect SkiBoard: {}".format(id))
            flash('We could not find a ski or board with that ID. Please try again.')

            return redirect('/')
        
        if collections:
            skiboard['collections'] = collections

        logging.info("Collecting SkiBoard Data:\n{}".format(skiboard))
        return render_template('views/view.html', page_name='view', skiboard=skiboard, comparisons=SkiBoard.calc_comparisons())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S T A R T   C O M P A R E                      H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class StartCompareHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self):
        if not 'compare' in session:
            return render_template('views/compare.html', page_name='compare', comparisons=SkiBoard.calc_comparisons())
        
        # Build comparison URL from comparisons in session
        comparisons = session['compare']
        logging.info("Getting comparisons from session: {}".format(comparisons))
        suffix = ''
        for comparison in comparisons.keys():
            skiboard, sizes = SkiBoard.get_item_by_id(comparison)

            suffix += skiboard['slug']
            suffix += '['
            for size in session['compare'][comparison]:
                suffix += size + ','
            suffix = suffix[:-1]
            suffix += ']'
            suffix += '+'

        if not suffix:
            return render_template('views/compare.html', page_name='compare', comparisons=SkiBoard.calc_comparisons())

        suffix = suffix[:-1]
        logging.info("Redirecting to: /compare/{}".format(suffix))
        return redirect('/compare/{}'.format(suffix))
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A D D  T O   C O M P A R E                     H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class AddToCompareHandler(MethodView):
    # -------------------------------------- P O S T
    def post(self):

        r = request.get_json()
        resp = {
            'success': True,
            'msg': 'madeit',
            'request': r
        }

        # Collect skiboard data
        skiboard_id = r['skiboard']
        sizes_to_add = r['sizes']
        skiboard, sizes = SkiBoard.get_item_by_id(skiboard_id)
        logging.info("Found skiboard: {}\n\n with sizes: {}".format(skiboard, sizes))

        # Return if no matching firestore data
        if not skiboard or not sizes:
            resp['success'] = False
            resp['msg'] = "Could not find sizes in firestore"
            return resp
        
        # Compare requested sizes to those found in firestore
        for i, s in enumerate(sizes_to_add):
            found = False
            for size in sizes:
                if size['size'] == s:
                    found = True
                    break
            if not found:
                sizes_to_add.pop(i)
            

        # Return if no matching sizes
        if not sizes_to_add:
            resp['success'] = False
            resp['msg'] = "No sizes to add"
            return resp
        
        try:
            if not 'compare' in session:
                session['compare'] = {}

            if skiboard_id in session['compare']:
                session['compare'][skiboard_id] = list(set(session['compare'][skiboard_id] + sizes_to_add))
                logging.info("Combined sizes: {}".format(session['compare'][skiboard_id]))
            else:
                session['compare'][skiboard_id] = list(set(sizes_to_add))
        except Exception as e:
            logging.error(e)

        resp['compare'] = session['compare']
        resp['comparisons'] = SkiBoard.calc_comparisons()

        logging.info("Sessions Comparisions: {}".format(session['compare']))
        session.modified = True
        return resp
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# R E M O V E   C O M P A R I S O N              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RemoveComparisonHandler(MethodView):
    # -------------------------------------- P O S T
    def post(self):

        r = request.get_json()
        resp = {
            'success': True,
            'msg': 'madeit',
            'request': r
        }

        # Collect skiboard data
        skiboard_id = r['skiboard']
        size_to_remove = r['size']
        skiboard, sizes = SkiBoard.get_item_by_id(skiboard_id)
        logging.info("Found skiboard: {}\n\n with sizes: {}".format(skiboard, sizes))

        # Return if no matching firestore data
        if not skiboard or not sizes:
            resp['success'] = False
            resp['msg'] = "Could not find sizes in firestore"
            return resp
        
        found = False
        for size in sizes:
            if size['size'] == size_to_remove:
                found = True
                break

        if not found:
            resp['success'] = False
            resp['msg'] = "Requested size not found in firestore"
            return resp
        
        try:
            if not 'compare' in session:
                session['compare'] = {}

            if skiboard_id in session['compare']:
                session['compare'][skiboard_id].remove(size_to_remove)
                logging.info("Comparisons: {}".format(session['compare']))
        except Exception as e:
            logging.error(e)

        resp['compare'] = session['compare']
        resp['comparisons'] = SkiBoard.calc_comparisons()

        logging.info("Sessions Comparisions: {}".format(session['compare']))
        session.modified = True

        return resp

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C L E A R   C O M P A R I S O N S              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ClearComparisonsHandler(MethodView):
    # -------------------------------------- P O S T
    def post(self):    
        r = request.get_json()
        resp = {
            'success': True,
            'msg': 'madeit',
            'request': r
        }

        session['compare'] = {}
        session.modified = True
        logging.info("Clearing comparison from session: {}".format(session))
        return resp

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M P A R E   I T E M                        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CompareHandler(MethodView):
    # ---------------------------------------- G E T
    def get(self, slugs):

        logging.info("Session data: {}".format(session))

        if not slugs:
            return redirect('/')

        msg = "Collecting SkiBoard Data:"
        # Collect each item to be compared
        skiboards = []
        slugs = slugs.split('+')
        logging.info("Comparing SkiBoards:\n{}".format(slugs))
        for slug in slugs:
            if '[' not in slug or '[' not in slug:
                continue
            sizes = slug[slug.index('[') +1 : slug.index(']')]
            slug = slug.replace('[{}]'.format(sizes), '')
            sizes = sizes.split(',')
            logging.info("Slug: {}".format(slug))
            logging.info("Sizes: {}".format(sizes))
            skiboard, collections = SkiBoard.get_item_by_slug(slug)

            if not skiboard:
                continue
            else:
                if collections:
                    skiboard['collections'] = []
                    for collection in collections:
                        if 'size' in collection.keys() and collection['size'] in sizes:
                            skiboard['collections'].append(collection)

                skiboards.append(skiboard)

                msg += '\n{}'.format(skiboard)
    
        logging.info(msg)
        if not skiboards:
            session['compare'] = {}
            session.modified = True
            return redirect('/compare')
        
        return render_template('views/compare.html', page_name='compare', skiboards=skiboards, comparisons=SkiBoard.calc_comparisons())
    