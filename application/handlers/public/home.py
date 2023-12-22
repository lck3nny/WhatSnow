import logging
import json
import pymysql

# Infrastructure Imports
# --------------------------------------------------
from flask import render_template, request
from flask.views import MethodView

# Model Imports
# --------------------------------------------------
from application.models.skiboard import SkiBoard

__author__ = 'liamkenny'

# --------------------------------------------------
# Validate Query                     F U N C T I O N
# --------------------------------------------------
def validate_query(query):
    return query

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# H O M E                                        H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class HomePageHandler(MethodView):
    # ---------------------------------------- G E T
    def get(request):
        # Database Setup
        # --------------------------------------------------
        #db = pymysql.connect("localhost", "username", "password", "database")
        f = open('./config/localdb_config.json')
        dbconfig = json.loads(f.read())
        for item in dbconfig:
            logging.info("Param: {} Value: {}\n".format(item, dbconfig[item]))

        db = pymysql.connect(host=dbconfig['localhost'], user=dbconfig['username'], password=dbconfig['password'], database=dbconfig['database'])
        f.close()

        cursor = db.cursor()
        sql = "SELECT * FROM Users"
        cursor.execute(sql)
        results = cursor.fetchall()
        logging.info("MySQL Test:\n{}".format(results))

        return render_template('core/index.html', page_name='index', comparisons=SkiBoard.calc_comparisons())
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# S E A R C H                                    H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SearchHandler(MethodView):
    # ---------------------------------------- G E T
    def get(request):

        return True
    
    # -------------------------------------- P O S T
    def post(self):
        r = request.get_json()
        query = r['query']

        # Check input for XSS
        if not validate_query(query):
            return {
                'success': False,
                'valid': False
            }
        
        try:
            # Query ElasticSearch
            results = SkiBoard.search(query)
            logging.info("Search: {}\nResults: {}".format(query, results))
        except Exception as e:
            logging.error("Problem searching for query: {}... {}".format(query, e))
            return {
                'success': False,
                'msg': e
            }
        
        return {
            'success': True,
            'query': r,
            'results': results,
            'valid': True
        }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# C O M I N G   S O O N                          H A N D L E R
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ComingSoonHandler(MethodView):
    # ---------------------------------------- G E T
    def get(request):
        return render_template('core/coming_soon.html', page_name='comingsoon', comparisons=SkiBoard.calc_comparisons())

    