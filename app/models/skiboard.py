import os.path
import logging
import json
import pytz
from datetime import datetime
from operator import itemgetter
from difflib import SequenceMatcher

# Application Imports
# --------------------------------------------------
from app.core import setupdb, db


# Infrastructure Imports
# --------------------------------------------------
from flask import session
from firebase_admin import firestore
#from elasticsearch import Elasticsearch
#from elasticsearch.client import IndicesClient





__author__ = 'liamkenny'

unit_names = {
    'size':             ['size', 'length'],
    'nose_width':       ['nose width', 'tip width'],
    'waist_width':      ['waist width'],
    'tail_width':       ['tail width'],
    'sidecut':          ['sidecut', 'sidecut radius', 'turning radius'],
    'effective_edge':   ['effective edge', 'running length'],
    'setback':          ['stance setback'],
    'stance width':     ['stance width', 'stance range'],
    'profile':          ['bend', 'profile'],
    'flex':             ['flex', 'stiffness'],
    'asym':             ['asym', 'asymetric']
}

profile_types = {
    'full_camber': 'url_for_img',
    'hybrid_camber': 'url_for_img',
    'directional_camber': 'url_for_img',
    'flat': 'url_for_img',
    'directional_flat': 'url_for_img',
    'hybrid_rocker': 'url_for_img',
    'full_rocker': 'url_for_img'
}

param_names = ['size', 'nose_width', 'waist_width', 'tail_width', 'sidecut', 'effective_edge', 'setback', 'stance_width']

# Connect ElasticSearch credentials
f = open(os.path.dirname(__file__) + '/../config/bonsai_config.json')
es_config = json.load(f)


# --------------------------------------------------
# Match Param                        F U N C T I O N
# --------------------------------------------------
def match_param(param):

    # Calculate best similarity score for each unit name
    match_scores = {}
    for unit in unit_names:
        match_scores[unit] = 0
        for option in unit_names[unit]:
            similarity = SequenceMatcher(None, param.replace('_', ' '), option).ratio()
            #logging.info("param: {} - comparedto: {} - score: {}".format(param, option, similarity))
            if similarity > match_scores[unit]:
                match_scores[unit] = similarity
            
    matched = max(match_scores, key=match_scores.get)
    confidence = match_scores[max(match_scores)]
    #logging.info("Parameter Matching for: {} - best match: {}\n{}".format(param, matched, match_scores))

    return matched, confidence

# ==================================================
# S K I B O A R D                          C L A S S
# ==================================================
class SkiBoard():


    # If a SkiBoard has an ID of 0 it has not been saved in the database
    def __init__(self, skiboard_id, brand, model, year, name, slug, category, family=None, description=None, stiffness=None, shape=None, flex_profile=None, camber_profile=None, camber_details=[], core=None, core_profiling=None, fibreglass=None, laminates=[], resin=None, base=None, edge_tech=None, topsheet=None, sidewall=None, inserts=None, asym=False, weight=0, womens=False, youth=False, url=None):
        self.id = skiboard_id
        self.brand = brand
        self.model = model
        self.year = year
        self.name = name
        self.slug = slug
        self.category = category
        self.description = description
        self.stiffness = stiffness
        self.shape = shape
        self.family = family
        self.flex_profile = flex_profile
        self.camber_profile = camber_profile
        self.camber_details = camber_details
        self.core = core
        self.core_profiling = core_profiling
        self.fibreglass = fibreglass
        self.laminates = laminates
        self.resin = resin
        self.base = base
        self.edge_tech = edge_tech
        self.topsheet = topsheet
        self.sidewall = sidewall
        self.inserts = inserts
        self.asym = asym
        self.weight = weight
        self.womens = womens
        self.youth = youth
        self.url = url

    # --------------------------------------------------
    # Is Duplicate                       F U N C T I O N
    # --------------------------------------------------
    def is_duplicate(self):
        db = setupdb()
        cursor = db.cursor()

        # Search for SkiBoards with 
        try:
            logging.info("Checking for Duplicate SkiBoards: {} {} ({})".format(self.brand, self.model, self.year))
            sql = """SELECT skiboard_id FROM SkiBoards WHERE brand = '{}' AND model = '{}' AND year = '{}'""".format(self.brand, self.model, self.year)
            cursor.execute(sql)
            result = cursor.fetchone()
            logging.info("Duplicate Found: {}".format(result))
        except Exception as e:
            logging.error(e)

        if result:
            return True

        return False

    # --------------------------------------------------
    # Get Item                           F U N C T I O N
    # --------------------------------------------------
    @classmethod
    def get(cls, id=None, brand=None, model=None, year=None, slug=None):
        
        db = setupdb()
        cursor = db.cursor()

        if id:
            try:
                logging.info("Getting SkiBoard from ID: {}".format(id))
                sql = f"""SELECT * FROM SkiBoards WHERE skiboard_id = '{id}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))
            except Exception as e:
                logging.error(e)
                return None
            
        elif brand and model and year:
            try:
                logging.info("Getting SkiBoard by B-M-Y: {} {} ({})".format(brand, model, year))
                sql = f"""SELECT * FROM SkiBoards WHERE brand = '{brand}' AND model = '{model}' AND year = '{year}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))
            except Exception as e:
                logging.error(e)
                return None
        elif slug:
            try:
                sql = f"""SELECT * FROM SkiBoards WHERE slug = '{slug}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
            except Exception as e:
                logging.error(f"Could not get SkiBoard from Slug:\n{e}")
                return None
            
        if not result:
            return None
        
        # Map DB Result to User Object
        skiboard = SkiBoard(
            skiboard_id=result[0], 
            url=result[1], 
            brand=result[2], 
            model=result[3], 
            year=result[4], 
            name=result[5],
            slug=result[6],
            category=result[7],
            family=result[8],
            description=result[9],
            stiffness=result[10],
            flex_profile=result[11],
            camber_profile=result[12],
            camber_details=result[13],
            core=result[14],
            core_profiling=result[15],
            fibreglass=result[16],
            laminates=result[17],
            resin=result[18],
            base=result[19],
            edge_tech=result[20],
            topsheet=result[21],
            sidewall=result[22],
            inserts=result[23],
            asym=result[24],
            weight=result[25],
            womens=result[26],
            youth=result[27]
        )
        
        return skiboard


    # --------------------------------------------------
    # Save SkiBoard                      F U N C T I O N
    # --------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()

        try:
            if self.id:
                print("Updating SkiBoard...")
                sql = f"""REPLACE INTO SkiBoards (skiboard_id, url, brand, model, year, name, slug, category, family, description, stiffness, flex_profile, camber_profile, camber_details, core, laminates, base, sidewall, weight, youth, updated) 
                values(
                '{str(self.id)}'
                '{str(self.url)}', 
                '{str(self.brand)}',  
                '{str(self.model)}', 
                '{str(self.year)}',
                '{str(self.brand)} {str(self.model)} {str(self.year)}',
                '{str(self.brand).lower()}-{str(self.model).lower()}-{str(self.year)}',
                '{str(self.category)}', 
                '{str(self.family)}', 
                '{str(self.description)}', 
                {float(self.stiffness)}, 
                '{str(self.flex_profile)}', 
                '{str(self.camber_profile)}', 
                '{'~'.join(str(i) for i in self.camber_details)}', 
                '{str(self.core)}', 
                '{'~'.join(str(i) for i in self.laminates)}', 
                '{str(self.base)}', 
                '{str(self.sidewall)}', 
                {float(self.weight)}, 
                {bool(self.youth)}, 
                '{datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")}' )"""
                
            else:
                print("Creating SkiBoard...")
                sql = f"""INSERT INTO SkiBoards (url, brand, model, year, name, slug, category, family, description, stiffness, flex_profile, camber_profile, camber_details, core, laminates, base, sidewall, weight, youth, created, updated) 
                values(
                '{str(self.url)}', 
                '{str(self.brand)}', 
                '{str(self.model)}', 
                '{str(self.year)}', 
                '{str(self.brand)} {str(self.model)} {str(self.year)}',
                '{str(self.brand).lower()}-{str(self.model).lower()}-{str(self.year)}',
                '{str(self.category)}', 
                '{str(self.family)}', 
                '{str(self.description)}', 
                {float(self.stiffness)}, 
                '{str(self.flex_profile)}', 
                '{str(self.camber_profile)}', 
                '{'~'.join(str(i) for i in self.camber_details)}', 
                '{str(self.core)}', 
                '{'~'.join(str(i) for i in self.laminates)}', 
                '{str(self.base)}', 
                '{str(self.sidewall)}', 
                {float(self.weight)}, 
                {int(bool(self.youth))}, 
                '{datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")}',
                '{datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")}')"""
                
            
            print(f"About to execute SQL: {sql}")
            cursor.execute(sql)
            db.commit()
             
        except Exception as e:
            logging.error("Could not create new SkiBoard:\n{}".format(e))
            print("Could not create new SkiBoard: {}".format(e))
            return False

        logging.info("Saved SkiBoard:\nBrand: {}\nModel: {} Year: ({})".format(self.brand, self.model, self.year))

        # ToDo...
        # Update ElasticSearch
        '''
        successes = 0
        logging.info("Uploading SkiBoard to ElasticSearch")
        es.update(
            id=self.id,
            index='SkiBoards',
            document=self.__dict__
        )   
        '''
        

        return True
    
    # --------------------------------------------------
    # Search Database                    F U N C T I O N
    # -------------------------------------------------- 
    @classmethod
    def search_db(cls, query_string):
        
        db = setupdb()
        cursor = db.cursor()

        try:
            #logging.info("Searching for SkiBoard: {}".format(query_string))
            print(f"Searching for SkiBoard: {query_string}")
            sql = f"SELECT * FROM SkiBoards WHERE MATCH(name) AGAINST('{query_string}' IN NATURAL LANGUAGE MODE)"
            # sql = f"SELECT * FROM SkiBoards WHERE MATCH(name) AGAINST('{query_string}' WITH QUERY EXPANSION)"
            cursor.execute(sql)
            response = cursor.fetchall()
            logging.info("Response: {}".format(response))
            print(f"Response: {response}")
        except Exception as e:
            logging.error(e)
            return None
    
        results = []
        for r in response:
            logging.info(f"Extracting skiboard from result: \n{r}")
            # Map DB Result to User Object
            result = SkiBoard(
                skiboard_id=r[0], 
                url=r[1], 
                brand=r[2], 
                model=r[3], 
                year=r[4], 
                name=r[5],
                slug=r[6],
                category=r[7],
                family=r[8],
                description=r[9],
                stiffness=r[10],
                flex_profile=r[11],
                camber_profile=r[12],
                camber_details=r[13],
                core=r[14],
                core_profiling=r[15],
                fibreglass=r[16],
                laminates=r[17],
                resin=r[18],
                base=r[19],
                edge_tech=r[20],
                topsheet=r[21],
                sidewall=r[22],
                inserts=r[23],
                asym=r[24],
                weight=r[25],
                womens=r[26],
                youth=r[27]
            )

            logging.info(f"Results: \n{result.__dict__}")
            results.append(result)

        return results
    


    # --------------------------------------------------
    # Update ElasticSearch               F U N C T I O N
    # --------------------------------------------------
    def update_es(id, skiboard, es_index='skiboards'):

        if not skiboard:
            return False

        # Connect to ElasticSearch
        es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))
        idx_manager = IndicesClient(es_client)
        active_index = list(idx_manager.get(es_index).keys())[0]

        # Create or Update document
        if not es_client.exists(index=es_index, id=id):
            return es_client.index(index=active_index, id=id, body=skiboard.__dict__)

        return es_client.update(index=active_index, id=id, document=skiboard)
       
    
    # --------------------------------------------------
    # Search ElasticSearch               F U N C T I O N
    # --------------------------------------------------
    @classmethod
    def search_es(query, es_index='skiboards'):
         # Connect to ElasticSearch
        try:
            logging.info(f"ElasticSearch...\nES URL: {es_config['url']}\nBasic Auth: {es_config['key']} - {es_config['secret']}")
            es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))

            logging.info(list(es_client.indices.get_alias(index="*"))[0])
            active_index = list(es_client.indices.get_alias(index="*"))[0]
            
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "type": "bool_prefix",
                        "fields": [
                            "name",
                            "brand",
                            "model"
                        ]
                    }
                }
            }
        except Exception as e:
            logging.error(f"WTF:\n{e}")

        logging.info("Querying elasticsearch index {}: \n{}".format(active_index, search_body))
        resp = es_client.search(index="skiboards-2024-02-21", body={"query": {"match_all": {}}})

        #resp = es_client.search(index='SkiBoards', body={"query": {"match_all": {}}})
        logging.info("ElasticSearch response: {}".format(resp))
        res = []
        try:
            for hit in resp['hits']['hits']:
                skiboard = SkiBoard(
                    skiboard_id = hit['_source']['skiboard_id'], 
                    url = hit['_source']['url'], 
                    brand = hit['_source']['brand'], 
                    model = hit['_source']['model'], 
                    year = hit['_source']['year'], 
                    name = hit['_source']['name'],
                    slug = hit['_source']['slug'],
                    category = hit['_source']['category'],
                    family = hit['_source']['family'],
                    description = hit['_source']['description'],
                    stiffness = hit['_source']['stiffness'],
                    flex_profile = hit['_source']['flex_profile'],
                    camber_profile = hit['_source']['camber_profile'],
                    camber_details = hit['_source']['camber_details'],
                    core = hit['_source']['core'],
                    core_profiling = hit['_source']['core_profile'],
                    fibreglass = hit['_source']['fibreglass'],
                    laminates = hit['_source']['laminates'],
                    resin = hit['_source']['resin'],
                    base = hit['_source']['base'],
                    edge_tech = hit['_source']['edge_tech'],
                    topsheet = hit['_source']['topsheet'],
                    sidewall = hit['_source']['sidewall'],
                    inserts = hit['_source']['inserts'],
                    asym = hit['_source']['asym'],
                    weight = hit['_source']['weight'],
                    womens = hit['_source']['womens'],
                    youth = hit['_source']['youth']
                )

                res.append(skiboard)
        except Exception as e:
            logging.error("Error extracting hits from ElasticSearch: {}".format(e))
            
        logging.info("ElasticSearch:\nQuery: {}\nResponse: {}".format(query, res))
        
        return res

    # --------------------------------------------------
    # Calculate Comparisons              F U N C T I O N
    # --------------------------------------------------
    def calc_comparisons():
        total_comparisons = 0
        logging.info("Session: {}".format(session))
        if 'compare' in session and session['compare']:
            for key in session['compare']:
                total_comparisons += len(session['compare'][key])

        return "[ {} ]".format(total_comparisons)


    # --------------------------------------------------
    # Extract Params from Text           F U N C T I O N
    # --------------------------------------------------
    def extract_params_from_text(raw_input):
        # Initialise empty dictionaries
        sizes = 0
        params = {}
        param_units = {}

        logging.info("Extracting params from raw input")

        # Itterate throguh each row
        for row in raw_input.split('\n'):
            split_row = row.split(" ")

            # Extract name from row
            row_name = " ".join(split_row[:-1])

            logging.info("Split row: {}".format(split_row))
            logging.info("Row name: {}".format(row_name))

            # Extract unit from row
            if '(' in str(row):
                units = str(row)[row.find('(') +1:row.find(')')]
            else:
                units = None

            # Extract values from row
            values = split_row[-1].split('\t')[1:]

            # Remove rogue characters
            for x, v in enumerate(values):
                values[x] = v.replace('\r', '')

            # Create dict for params and units
            params[row_name.replace(' ', '_').lower()] = values
            param_units[row_name.replace(' ', '_').lower()] = units

            sizes += 1
            
        return params, param_units, sizes


    # --------------------------------------------------
    # Format Params                      F U N C T I O N
    # --------------------------------------------------
    def format_params(unformatted, units):
        formatted_data = {}
        formatted_units = {}
        data_confidence = {}

        # Populate formatted dictionaries with given data
        for key in unformatted:
            matched, confidence = match_param(key)
            if matched not in data_confidence or (matched in data_confidence and confidence > data_confidence[matched]):
                #logging.info("Updating param matching...\nKey: {} - Confidence: {}\nDict: {}".format(matched, confidence, data_confidence))
                data_confidence[matched] = confidence
                formatted_data[matched] = unformatted[key]
                formatted_units[matched] = units[key]

        return formatted_data, formatted_units


    # --------------------------------------------------
    # Describe                           F U N C T I O N
    # --------------------------------------------------
    def describe():
        return {'profile_types': profile_types, 'unit_names': unit_names, 'param_names': param_names}
