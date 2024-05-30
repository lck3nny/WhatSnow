import logging

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.models.skiboard import SkiBoard
from app.models.user import User

# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView


__author__ = 'liamkenny'


# E X T R A C T   P A R A M                    F U N C T I O N   
# ------------------------------------------------------------
# Extracts the param range from a raw input
# --- input may contain a range: 1 - 3  OR  < 5  etc
# ------------------------------------------------------------
def extract_param(param):
    if not param: 
        return {'operator': None, 'val': None, 'delimiter': None}
    
    params = []
    # Split list of params 
    if ',' in param:
        params = param.replace(', ', ',').split(',')
        return {'operator': 'IN', 'val': params, 'delimiter': "IN"}

    # Split closed range of params
    if '-' in param:
        params = param.split('-')
        return {'operator': 'BETWEEN', 'val': params, 'delimiter': "AND"}
    
    # Split open range of params
    # This can be done better!
    # Let's look at where the comparitave sits for cases like: 2020> vs <2020
    if '<=' in param:
        return {'operator': '<=', 'val': param.replace('<=', ''), 'delimiter': ","}
    if '<' in param:
        return {'operator': '<', 'val': param.replace('<', ''), 'delimiter': ","}
    
    if '>=' in param:
        return {'operator': '>=', 'val': param.replace('>=', ''), 'delimiter': ","}
    if '>' in param:
        return {'operator': '>', 'val': param.replace('>', ''), 'delimiter': ","}
    
    
    return {'operator': '=', 'val': param}

    
# V A L I D A T E   Q U E R Y                  F U N C T I O N   
# ------------------------------------------------------------
# Type Check / XSS Check
# ------------------------------------------------------------
def validate_param(param):
    valid_param_types = {
        'brand': type("Burton"),
        'model': type("Hometown Hero"),
        'year': type(2020),
        'family': type("Family Tree"),
        'stiffness': type(6),
        'shape': type("Directional"),
        'flex_profile': type("Directional"),
        'camber_profile': type("Directional Camber"),
        'inserts': type("channel"),
        'category': type("Snowboard"),
        'length': type(160.0),
        'nose_width': type(307.7),
        'waist_width': type(258.0),
        'tail_width': type(295.7),
        'effective_edge': type(1217.0)
    }

    # madeit
    # how do we get the name of the param from the passsed object?
    # do we need to send both the key and data seperately as vars?

    return "Testing"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A D V A N C E D   S E A R C H                  H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdvancedSearchHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(r):
        default_params = {}
        if 'a_search' in session:
            default_params = session['a_search']
            # get default params


        return render_template('search/advanced_search.html', default_params=default_params, page_name='advanced search', comparisons=SkiBoard.calc_comparisons())
    
    # ------------------------------------------------ P O S T
    def post(self):
        logging.info("Advanced Search...")
        params = {"SkiBoards": None, "Sizes": None}
        r = request.get_json()
        logging.info(f"Request: \n {r}")
        
        # Return unsuccessful query for invalid params
        # Invalid params will be removed from object. Empty object indicates no queryable params.
        if not params:
            return {'success': False, 'query': f"No params provided", 'results': [], 'valid': False}
        

        # Extract SkiBoard params from equalities provided in form
        try:
            params['SkiBoards'] = {
                'year': extract_param(r['year']),
                'category': extract_param(r['category']),
                'stiffness': extract_param(r['stiffness']),
                'shape': extract_param(r['shape']),
                'camber_profile': extract_param(r['camber_profile'])
            }
            logging.info(f"Skiboard Params: {params['SkiBoards']}")
        except Exception as e:
            logging.error(f"Could not extract SkiBoard Params: \n{e}")
            return  {'success': False, 'query': {"skiboard_params": None}, 'results': [None], 'valid': True}
        
        # Extract Size params from in/equalities provided in form
        try:
            params['Sizes'] = {
                'length': extract_param(r['length']),
                'nose_width': extract_param(r['nose_width']),
                'waist_width': extract_param(r['waist_width']),
                'tail_width': extract_param(r['tail_width']),
                'effective_edge': extract_param(r['effective_edge'])
            }
            logging.info(f"Size Params: {params['Sizes']}")
        except Exception as e:
            logging.error(f"Could not extract Size Params: \n{e}")
            return  {'success': False, 'query': {"skiboard_params": params['SkiBoards'], "size_params": params['Sizes']}, 'results': [None], 'valid': True}

        # Search for results using extracted params
        try:
            logging.info("Querying Database...") 
            logging.info(f"Params: {params}")  
            results, query = SkiBoard.advanced_search(params)
        except Exception as e:
            logging.error(f"There was a problem running the Advanced Search: {e}")
        
        skiboards = [res['skiboard'].__dict__ for res in results]
        sizes = [res['size'] for res in results]
        for x, skiboard in enumerate(skiboards):
            skiboard['size'] = sizes[x]

        # Return results in JSON format
        return {
            'success': bool(skiboards),
            'query': query,
            'results': skiboards,
            'valid': True
        }
    