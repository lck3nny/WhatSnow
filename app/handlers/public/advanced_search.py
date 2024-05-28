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
    query = "SELECT SkiBoards.skiboard_id, SkiBoards.brand, SkiBoards.model, SkiBoards.year Sizes.size FROM SkiBoards INNER JOIN SkiBoards ON SkiBoards.skiboard_id = Sizes.skiboard_id"
    if data['SkiBoards'] or data['Sizes']:
        query += " WHERE "
        # Loop through each table to query (SkiBoards, Sizes)
        for table in data:
            for param in data[table]:
                if data[table][param]['val']:
                    empty = False
                    # Append list of filters
                    if data[table][param]['operator'] == "IN":
                        s = ", ".join(data[table][param]['val'])
                        query += f" {table}.{param} {data[table][param]['operator']} ({s})"
                    # Append a range of filters
                    elif data[table][param]['operator'] == "BETWEEN":
                        query += f" {table}.{param} {data[table][param]['operator']} {data[table][param]['val'][0]} AND {data[table][param]['val'][-1]}"
                    # Append specific value filters
                    else:
                        query += f" {table}.{param} {data[table][param]['operator']} {data[table][param]['val']}"
    
    if not empty:
        return query
    else:
        return ""


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
        logging.info("FUCK YOUR COOKIES")
        r = request.get_json()
        logging.info(f"Request: \n {r}")

        '''
        # Check input for XSS
        if not validate_query(query):
            return {
                'success': False,
                'valid': False
            }
        '''
        params = {"SkiBoards": None, "Sizes": None}

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


        # Build query from provided param in/equalities 
        logging.info("Querying Database...") 
        logging.info(f"Params: {params}")  
        try:
            query = build_query(params)
            logging.info(f"Query: {query}")
        except Exception as e:
            logging.error(f"Unable to generate SQL query: {e}")

        if not query:
            logging.info("Empty query, not executing")
            return{
                'success': False,
                'query': query,
                'results': [],
                'valid': True
            }
        
        # Execute database query
        try:
            results = SkiBoard.search_db(query)
            logging.info(f"Search: {query}\nResults: {results}")
        except Exception as e:
            logging.error(f"Problem searching for query: {query}... {e}")
            return  {'success': False, 'query': params, 'results': [None], 'valid': True}

        # Return results in JSON format
        return {
            'success': bool(results),
            'query': query,
            'results': [r.__dict__ for r in results],
            'valid': True
        }