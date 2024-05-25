import logging

# Infrastructure Imports
# --------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
from app.models.skiboard import SkiBoard
from app.models.user import User

__author__ = 'liamkenny'

# Extracts the param range from a raw input
# --- input may contain a range: 1 - 3  OR  < 5  etc
def extract_param(param):
    if not param: 
        return {'type': 'empty', 'val': None}
    
    params = []
    # Split list of params 
    if ',' in param:
        params = param.split(',')
        return {'type': 'list', 'val': params}

    # Split closed range of params
    if '-' in param:
        params = param.split('-')
        return {'type': 'range', 'val': params}
    
    # Split open range of params
    if '<=' in param:
        return {'type': 'lessthaninclusive', 'val': param.replace('<=', '')}
    if '<' in param:
        return {'type': 'lessthan', 'val': param.replace('<', '')}
    
    if '>=' in param:
        return {'type': 'greaterthaninclusive', 'val': param.replace('>=', '')}
    if '>' in param:
        return {'type': 'greaterthan', 'val': param.replace('>', '')}
    
    
    return {'type': 'error', 'val': None}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A D V A N C E D   S E A R C H                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdvancedSearchHandler(MethodView):
    # ---------------------------------------- G E T
    def get(r):
        default_params = {}
        if 'a_search' in session:
            default_params = session['a_search']
            # get default params


        return render_template('search/advanced_search.html', default_params=default_params, page_name='advanced search', comparisons=SkiBoard.calc_comparisons())
    
    # -------------------------------------- P O S T
    def post(self):
        r = request.get_json()
        query = r['query']

        '''
        # Check input for XSS
        if not validate_query(query):
            return {
                'success': False,
                'valid': False
            }
        '''

        skiboard_params = {
            'year': {extract_param(r['year'])},
            'category': extract_param(r['category']),
            'stiffness': extract_param(r['stiffness']),
            'shape': extract_param(r['shape']),
            'camber_profile': extract_param(r['camber_profile'])
        }

        size_params = {
            'length': extract_param(r['length']),
            'nose_width': extract_param(r['nose_width']),
            'waist_width': extract_param(r['waist_width']),
            'tail_width': extract_param(r['tail_width']),
            'effective_edge': extract_param(r['effective_edge'])
        }

        # madeit
        # Generate SQL string for querying based on param and param type

        # Query DB
        logging.info("Querying Database...")        
        try:
            results = SkiBoard.search_db(query)
            #results = SkiBoard.search_es(query)
            logging.info(f"Search: {query}\nResults: {results}")
        except Exception as e:
            logging.error(f"Problem searching for query: {query}... {e}")
        

        return {
            'success': bool(results),
            'query': r,
            'results': [r.__dict__ for r in results],
            'valid': True
        }