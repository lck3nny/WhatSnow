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
        params = param.split(',')
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



# B U I L D   Q U E R Y                        F U N C T I O N   
# ------------------------------------------------------------
# Generates the SQL query for 
# querying using advanced search params
# ------------------------------------------------------------
def build_query(data):
    empty = True
    query = "SELECT SkiBoards.skiboard_id, brand, model, year, size FROM SkiBoards INNER JOIN Sizes ON SkiBoards.skiboard_id = Sizes.skiboard_id"
    if data['SkiBoards'] or data['Sizes']:
        first = True
        query += " WHERE "
        # Loop through each table to query (SkiBoards, Sizes)
        for table in data:
            for param in data[table]:
                if data[table][param]['val']:
                    if not validate_param(data[table][param]):
                        continue

                    empty = False
                    # Append list of filters
                    # WHERE camber_profile IN (Full Camber, Hybrid Camber, Directional Camber)
                    if data[table][param]['operator'] == "IN":
                        s = ", ".join(data[table][param]['val'])
                        query += f" {param} {data[table][param]['operator']} ({s})"

                    # Append a range of filters
                    # WHERE waist_width BETWEEN 250 AND 260
                    elif data[table][param]['operator'] == "BETWEEN":
                        query += f" {param} {data[table][param]['operator']} {data[table][param]['val'][0]} AND {data[table][param]['val'][-1]}"
                    
                    # Append specific value filters
                    # WHERE model = Deep Thinker
                    else:
                        query += f" {param} {data[table][param]['operator']} '{data[table][param]['val']}'"
            if not first:
                query += " AND "    
                
        # Example Query String:
        # ....................................................
        # SELECT SkiBoards.skiboard_id, brand, model, year, size
        # FROM SkiBoards INNER JOIN Sizes ON SkiBoards.skiboard_id = Sizes.skiboard_id 
        # WHERE model = 'Custom'AND waist_width > 250;
        # ....................................................

        # Problem Query String:
        # ....................................................
        # SELECT SkiBoards.skiboard_id, SkiBoards.brand, SkiBoards.model, SkiBoards.year Sizes.size 
        # FROM SkiBoards INNER JOIN SkiBoards ON SkiBoards.skiboard_id = Sizes.skiboard_id 
        # WHERE  SkiBoards.year = custom
        # ....................................................


    if not empty:
        return f"{query};"
    else:
        return ""
    
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
    
        # Return results in JSON format
        return {
            'success': bool(results),
            'query': query,
            'results': [r.__dict__ for r in results],
            'valid': True
        }