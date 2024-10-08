import logging

# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import render_template, redirect, flash, session, request
from flask.views import MethodView

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.models.skiboard import SkiBoard
from app.models.size import Size

__author__ = 'liamkenny'

item_names = ['asym']

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# V I E W   I T E M                              H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ViewHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self, slug):

        user=None
        if 'user' in session:
            logging.info("View SkiBoard User")
            user = session['user']
            logging.info(f"User: {user}")
            logging.info(f"User permissions: {user['permissions']}")
        
        skiboard = SkiBoard.get(slug=slug)
        if not skiboard:
            logging.error(f"Could not collect SkiBoard: {slug}")
            flash('We could not find the ski or snowboard that you were looking for. Please try again later.')
            return redirect('/')
    
        try:
            sizes = Size.get(skiboard.id)
            for x, size in enumerate(sizes):
                sizes[x] = size.__dict__

            logging.info(f"Sizes for {skiboard.name}:\n{sizes}")
        except Exception as e:
            logging.error(f"Could not get sizes for skiboard ({skiboard.name}): \n{e}")

        logging.info("Collecting SkiBoard Data:\n{}".format(skiboard))
        return render_template('views/view.html', user=user, page_name='view', skiboard=skiboard.__dict__, sizes=sizes, comparisons=SkiBoard.calc_comparisons(), )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S T A R T   C O M P A R I S O N                H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class StartCompareHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(self):
        if not 'compare' in session:
            return render_template('views/compare.html', page_name='compare', comparisons=SkiBoard.calc_comparisons())
        
        # Build comparison URL from comparisons in session
        comparisons = session['compare']
        logging.info("Getting comparisons from session: {}".format(comparisons))
        suffix = ''
        for skiboard_id in comparisons.keys():
            skiboard = SkiBoard.get(id=skiboard_id)
            logging.info(f"Found SkiBoard:\n{skiboard.__dict__}")
            sizes = Size.get(skiboard_id=skiboard_id)

            suffix += skiboard.slug
            suffix += '['
            for size in session['compare'][skiboard_id]:
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
# A D D  T O   C O M P A R I S O N               H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
class AddToCompareHandler(MethodView):
    # ------------------------------------------------ P O S T
    def post(self):

        r = request.get_json()
        resp = {
            'success': True,
            'msg': 'madeit',
            'request': r
        }

        # Check if comparisons are maxxed out
        if SkiBoard.calc_comparisons() >= 10:
            resp['success'] = False
            resp['msg'] = "Compasison max reached"
            return resp

        try:
            logging.info(f"Adding skiboard sizes to comparisons:\n{r}")
            # Collect skiboard data
            skiboard_id = r['skiboard']
            sizes_to_add = r['sizes']

            skiboard = SkiBoard.get(id=skiboard_id)
            sizes = Size.get(skiboard_id=skiboard_id)
            logging.info("Found skiboard: {}\n\n with sizes: {}".format(skiboard, sizes))
        except Exception as e:
            logging.error(f"ERROR: {e}")
        
        try:
            # Return if no matching firestore data
            if not skiboard or not sizes:
                resp['success'] = False
                resp['msg'] = "Could not find sizes in firestore"
                logging.error("Could not find sizes for skiboard")
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
        except Exception as e:
            logging.error(f"ERROR: {e}")
            

        # Return if no matching sizes
        if not sizes_to_add:
            resp['success'] = False
            resp['msg'] = "No sizes to add"
            logging.error("No sizes to add")
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
    # ------------------------------------------------ P O S T
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

        logging.info(f"Removing SkiBoard from comparisons list: {skiboard_id}: {size_to_remove}")
        
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
    # ------------------------------------------------ P O S T
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
    # -------------------------------------------------- G E T
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
            skiboard = SkiBoard.get(slug=slug)
            all_sizes = Size.get(skiboard_id=skiboard.id)
            #skiboard, collections = SkiBoard.get_item_by_slug(slug)

            if not skiboard:
                continue
            else:
                logging.info(f"Filtering sizes by: {sizes}")
                skiboard.sizes = []
                for s in all_sizes:
                    if s.size in sizes:
                        logging.info(f"Adding size to skibaord ({skiboard.name})\n{s.__dict__}")
                        skiboard.sizes.append(s.__dict__)

                skiboards.append(skiboard)

                msg += '\n{}'.format(skiboard)
    
        logging.info(msg)
        if not skiboards:
            session['compare'] = {}
            session.modified = True
            return redirect('/compare')
        
        return render_template('views/compare.html', page_name='compare', skiboards=skiboards, comparisons=SkiBoard.calc_comparisons())
    