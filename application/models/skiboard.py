import os.path
import logging
import json
import pytz
from datetime import datetime
from operator import itemgetter
from difflib import SequenceMatcher

from flask import session

from application.core import setupdb



# Infrastructure Imports
# --------------------------------------------------
from firebase_admin import firestore
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient



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
# Slugify                            F U N C T I O N
# --------------------------------------------------
def slugify(strings):
    return '-'.join(strings).lower()

# --------------------------------------------------
# Nameify                            F U N C T I O N
# --------------------------------------------------
def nameify(strings):
    for s in strings:
        try:
            s = normaise_brand_model(s)
        except:
            continue

    return ' '.join(strings)


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

# --------------------------------------------------
# Normalise Brand / Model Names      F U N C T I O N
# --------------------------------------------------
def normaise_brand_model(s):
    normalised = ''
    s_split = s.split(' ')
    for word in s_split:
        if len(word) > 1:
            normalised += word[0].upper() + word[1:] + ''
        else:
            normalised += word.upper() + ''
    
    return normalised.strip()

class SkiBoard():

    # If a SkiBoard has an ID of 0 it has not been saved in the database
    def __init__(self, skiboard_id, brand, model, year, category, description=None, stiffness=None, family=None, flex_profile=None, camber_profile=None, camber_details=[], core=[], laminates=[], base=None, sidewall=None, weight=None, url=None):
        self.id = skiboard_id
        self.brand = brand
        self.model = model
        self.year = year
        self.category = category
        self.description = description
        self.stiffness = stiffness
        self.family = family
        self.flex_profile = flex_profile
        self.camber_profile = camber_profile
        self.camber_details = camber_details
        self.core = core
        self.laminates = laminates
        self.base = base
        self.sidewall = sidewall
        self.weight = weight
        #self.url = url

    # --------------------------------------------------
    # Is Duplicate                       F U N C T I O N
    # --------------------------------------------------
    def is_duplicate(self):
        db = setupdb()
        cursor = db.cursor()

        # Search for SkiBoards with 
        try:
            logging.info("Checking for Duplicate SkiBoards: {}".format(self.id))
            sql = """SELECT * FROM SkiBoards WHERE brand = '{}' AND model = '{}' AND year = '{}'""".format(self.brand, self.model, self.year)
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
    def get(cls, id=None, brand=None, model=None, year=None):
        
        db = setupdb()
        cursor = db.cursor()

        if id:
            try:
                logging.info("Getting SkiBoard from ID: {}".format(id))
                sql = """SELECT * FROM SkiBoards WHERE skiboard_id = '{}'""".format(id)
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))
            except Exception as e:
                logging.error(e)
                return None
            
        elif brand and model and year:
            try:
                logging.info("Getting SkiBoard by B-M-Y: {} {} ({})".format(brand, model, year))
                sql = """SELECT * FROM SkiBoards WHERE brand = '{}' AND model = '{}' AND year = '{}'""".format(brand, model, year)
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))
            except Exception as e:
                logging.error(e)
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
            category=result[5],
            family=result[6],
            description=result[7],
            stiffness=result[8],
            flex_profile=result[9],
            camber_profile=result[10],
            camber_details=result[11],
            core=result[12],
            laminates=result[13],
            base=result[14],
            sidewall=result[15],
            weight=result[16]
        )
        
        return skiboard


    # --------------------------------------------------
    # Save SkiBoard                    F U N C T I O N
    # --------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()

        try:
            sql = """REPLACE INTO 'Users' (user_id, fname, lname, email, ski, snowboard, stance, region, permissions, created, updated, photo)
                values ({}, {}, {}, {}, {}, {}, {}, {}))
            """.format(self.id, self.fname, self.lname, self.email, 
                       self.ski, self.snowboard, self.stance, self.region, '~'.join(self.permissions), 
                       datetime.now(pytz.timezone('Canada/Pacific')), datetime.now(pytz.timezone('Canada/Pacific')),
                       self.photo)
            cursor.execute(sql)
            db.commit()
            #self.id = cursor.execute("SELECT last_insert_rowid() FROM songs").fetchone()[0]
             
        except Exception as e:
            logging.error("Could not create new user:\n{}".format(e))   
            return False

        logging.info("Created New User:\n{} {} ~ {}\nPermissions: {}\nSki: {} Snowboard: ({})\n{}Region: {}"
                     .format(self.fname, self.lname, self.email, ', '.join(self.permissions), self.ski, self.snowboard, self.stance, self.region))

        return True


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
            return es_client.index(index=active_index, id=id, body=skiboard)

        return es_client.update(index=active_index, id=id, document=skiboard)


    # --------------------------------------------------
    # Search                             F U N C T I O N
    # --------------------------------------------------
    def search(query, es_index='skiboards'):
        
        # Connect to ElasticSearch
        es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))
        idx_manager = IndicesClient(es_client)
        active_index = list(idx_manager.get(es_index).keys())[0]

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
        logging.info("Querying elasticsearch: {}".format(search_body))
        resp = es_client.search(index=active_index, body=search_body)
        logging.info("ElasticSearch response: {}".format(resp))
        res = []
        try:
            for hit in resp['hits']['hits']:
                res.append({
                    'id': hit['_id'],
                    'brand': hit['_source']['brand'],
                    'model': hit['_source']['model'],
                    'year': hit['_source']['year'],
                    'slug': hit['_source']['slug']
                })
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
