import logging
import json
import pymysql

# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import render_template, redirect, flash, request, session
from flask.views import MethodView
from flask import render_template, request
from flask.views import MethodView

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.models.skiboard import SkiBoard
from app.core import setupdb


__author__ = 'liamkenny'

# V A L I D A T E   Q U E R Y                  F U N C T I O N
# ------------------------------------------------------------
def validate_query(query):

    checks = ["http", "fuck"]
    for check in checks:
        if check in query:
            return False
    
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# H O M E                                        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class HomePageHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(request):

        return render_template('core/index.html', page_name='index', comparisons=SkiBoard.calc_comparisons())
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S E A R C H                                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SearchHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(request):

        return True
    
    # ------------------------------------------------ P O S T
    def post(self):
        r = request.get_json()
        query = r['query']

        # Check input for XSS
        if not validate_query(query):
            return {
                'success': False,
                'valid': False
            }
        
        # Query DB
        logging.info("Querying ElasticSearch...")
        #results = SkiBoard.search_es(query)
        
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M I N G   S O O N                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ComingSoonHandler(MethodView):
    # -------------------------------------------------- G E T
    def get(request):
        return render_template('core/coming_soon.html', page_name='comingsoon', comparisons=SkiBoard.calc_comparisons())

    